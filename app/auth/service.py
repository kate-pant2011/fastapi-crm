# business logic
from app.config.security import verify_password, hash_password, JWTService
from app.config.config import ApplicationException
from app.database.branch import add_branch
from app.database.user import (
    get_user_by_email,
    add_user,
    add_user_role,
    get_user_by_id,
    update_user_password,
)
from app.database.refresh_token import (
    add_refresh_jwt,
    verify_refresh_jwt,
    get_refresh_by_jwt,
)
from app.database.refresh_token import (
    deactivate_user_refresh,
    deactivate_all_user_refresh,
    TokenReuseDetection,
)
import uuid
from dataclasses import dataclass


@dataclass
class AuthTokensDTO:
    access: str
    refresh: str | None
    change_password: bool


async def login_user(session, email, password, device):

    user = await get_user_by_email(session, email)
    if not user:
        raise ApplicationException("invalid Credentials: login or password", 401)

    if not user.is_active:
        raise ApplicationException("User is archived", 400, {"id": user.id})

    if not verify_password(password, user.password_hash):
        raise ApplicationException("invalid Credentials: login or password", 401)

    roles = list({role.name for role in user.roles})
    status = user.must_change_password
    active = user.is_active
    is_new = user.is_new

    jwt = JWTService()
    access_token = jwt.create_access(user.id, roles, status, active, is_new)

    if user.must_change_password:
        return AuthTokensDTO(access=access_token, refresh=None, change_password=True)

    jti = str(uuid.uuid4())
    refresh = jwt.create_refresh(user.id, jti)
    exp = refresh.exp

    await add_refresh_jwt(session, user.id, exp, jti, device)

    return AuthTokensDTO(
        access=access_token, refresh=refresh.token, change_password=False
    )


async def logout_user(session, refresh_jwt):

    decoded = JWTService().decode_token(refresh_jwt)
    refresh = await get_refresh_by_jwt(session, decoded.jti)

    if not refresh:
        raise ApplicationException("Refresh token not found", 401)

    await deactivate_user_refresh(session, refresh.user_id, refresh.jti)

    return {"result": True}


async def update_tokens(session, refresh_jwt, device):
    try:

        decoded = JWTService().decode_token(refresh_jwt)
        old_refresh = await verify_refresh_jwt(session, decoded.jti)

        if not old_refresh:
            raise ApplicationException("Refresh token not found", 401)

        user_id = old_refresh.user_id
        user = await get_user_by_id(session, user_id)

        if not user.is_active:
            raise ApplicationException("User is inactive error", 403)

        roles = list({role.name for role in user.roles})
        status = user.must_change_password
        active = user.is_active

    except TokenReuseDetection as e:
        async with session.begin():
            await deactivate_all_user_refresh(session, e.user_id)
        raise

    jti = str(uuid.uuid4())

    jwt = JWTService()
    access_token = jwt.create_access(user_id, roles, status, active)
    refresh = jwt.create_refresh(user_id, jti)

    await add_refresh_jwt(session, user_id, refresh.exp, jti, device)

    return AuthTokensDTO(
        access=access_token, refresh=refresh.token, change_password=False
    )


async def signup_user(session, user_data) -> dict:
    user_exists = await get_user_by_email(session, user_data.email)
    if user_exists:
        raise ApplicationException(f"Email {user_data.email} is already used", 400)

    password_validity = check_password(user_data.password)
    if password_validity:
        raise ApplicationException(f"The password is weak: {password_validity}", 400)

    new_company = await add_branch(session, user_data.inn, user_data.company)
    hashed_password = hash_password(user_data.password)
    new_user = await add_user(
        session,
        user_data,
        hashed_password,
        new_company.id,
        password_change=False,
    )
    await add_user_role(session, new_user, ["owner"])

    return {"company": user_data.company, "login": user_data.email, "reason": None}


async def change_user_password(session, user_id, password):
    user = await get_user_by_id(session, user_id)
    if not user:
        raise ApplicationException("invalid Credentials: login or password", 401)

    if not user.is_active:
        raise ApplicationException("User is archived", 400, {"id": user.id})

    if not user.must_change_password:
        raise ApplicationException(
            f"User {user.email} has not applied for password-change", 400
        )

    password_validity = check_password(password)
    if password_validity:
        raise ApplicationException(f"The password is weak: {password_validity}", 400)

    hashed_password = hash_password(password)

    await update_user_password(session, user, hashed_password)

    return user.email


def check_password(password):
    if len(password) < 8:
        return "too short"

    if len(password) > 16:
        return " too long"

    if not str.isascii(password):
        return "includes forbidden symbols"

    if not any(c.isdigit() for c in password):
        return "doesn't include digit"

    if not any(c.isalpha() for c in password):
        return "doesn't include letter"

    return None
