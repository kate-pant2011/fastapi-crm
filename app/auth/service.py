# business logic
import uuid
import logging
from app.config.security import verify_password, hash_password, JWTService
from app.config.config import ApplicationException, settings
from app.email.templates import send_change_password_email, send_suspicios_login_attempt_caution
from app.database.branch import add_branch
from app.database.user import (
    get_user_by_email,
    add_user,
    add_user_role,
    get_user_by_id,
    update_user_password,
    owner_exists
)
from app.database.refresh_token import (
    deactivate_user_refresh,
    deactivate_all_user_refresh,
    TokenReuseDetection,
    add_refresh_jwt,
    verify_refresh_jwt,
    get_refresh_by_jwt,
    
)
from app.database.reset_token import (
    add_reset_jwt, verify_reset_jwt, deactivate_all_user_reset_jwt, ResetTokenReuseDetection
)
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from app.audit.auth import auth_audit

logger = logging.getLogger(__name__)

@dataclass
class AuthTokensDTO:
    access: str
    refresh: str | None
    change_password: bool

@dataclass
class EmailConfigDTO:
    server: str
    port: int
    login: str


email = EmailConfigDTO(
    port = settings.SMTP_PORT,
    server = settings.SMTP_HOST,
    login = settings.EMAIL_USER
)

async def login_user(session, email, password, device, ip):
    user = await get_user_by_email(session, email)
    if not user:
        auth_audit.unknown_email_detected(email, ip, device)
        raise ApplicationException("invalid Credentials: login or password", 401)

    if not user.is_active:
        raise ApplicationException("User is archived", 400, {"id": user.id})

    now = datetime.now(timezone.utc)

    if user.locked_until and user.locked_until > now:
        raise ApplicationException(f"User has been blocked until {user.locked_until}", 403)
        
    if not verify_password(password, user.password_hash):
        user.failed_login_attempts += 1

        if user.failed_login_attempts >= 5:
            auth_audit.wrong_password_detected(user.email, ip, device)

            if user.locked_until is None or user.locked_until <= now:
                try:
                    await send_suspicios_login_attempt_caution(
                        to=user.email,
                        reason="авторизация"
                    )
                except Exception:
                    logger.exception(
                        "Failed to send security email"
                    )

            user.locked_until = (
                now + timedelta(minutes=15)
            )

        await session.commit()

        raise ApplicationException("invalid Credentials: login or password", 401)

    user.last_login_at = now
    user.last_login_ip = ip
    user.locked_until = None
    user.failed_login_attempts = 0

    roles = list({role.name for role in user.roles})
    status = user.must_change_password
    active = user.is_active

    jwt = JWTService()
    access_token = jwt.create_access(user.id, roles, status, active)

    if user.must_change_password:
        return AuthTokensDTO(access=access_token, refresh=None, change_password=True)

    jti = str(uuid.uuid4())
    refresh = jwt.create_refresh(user.id, jti)
    exp = refresh.exp

    await add_refresh_jwt(session, user.id, exp, jti, device)

    auth_audit.login_success(user.email, ip, device)
    return AuthTokensDTO(
        access=access_token, refresh=refresh.token, change_password=False
    )


async def logout_user(session, refresh_jwt):
    decoded = JWTService().decode_token(refresh_jwt)
    refresh = await get_refresh_by_jwt(session, decoded.jti)

    if not refresh:
        raise ApplicationException("Refresh token not found", 401)

    user_id = refresh.user_id

    try:
        await deactivate_user_refresh(session, user_id, refresh.jti)
    except Exception:
        logger.exception("failed to deactivate user refresh tokens", extra={"user_id": user_id})

    auth_audit.logout_success(user_id)
    return {"result": True}


async def update_tokens(session, refresh_jwt, device, ip):
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
        auth_audit.token_reuse_detected(e.user_id, ip)
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


async def signup_user(session, user_data, ip) -> dict:
    owner= await owner_exists(session)
    if owner:
        auth_audit.self_registration_attempt(
            user_data.email, ip
        )
        raise ApplicationException(f"Only admins can sign you up", 400)

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
        password_change=False
    )
    await add_user_role(
        session=session, 
        is_owner=True, 
        user=new_user, 
        new_roles=["owner"], 
        is_new=True
    )

    auth_audit.signup_success(user_data.email, ip)

    return {"company": user_data.company, "login": user_data.email, "reason": None}


async def change_user_password(session, user_id, password, ip):
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

    auth_audit.changed_password(user_id, ip)
    return user.email


def check_password(password):
    if len(password) < 8:
        return "too short"

    if len(password) > 16:
        return "too long"

    if not str.isascii(password):
        return "includes forbidden symbols"

    if not any(c.isdigit() for c in password):
        return "doesn't include digit"

    if not any(c.isalpha() for c in password):
        return "doesn't include letter"

    return None


async def create_password_reset_token(session, login, device, ip):
    user = await get_user_by_email(session, login.email)
    if not user:
        return {
            "message": "If an account with this email exists, password reset instructions have been sent."
        }

    jti = str(uuid.uuid4())

    jwt = JWTService()
    reset_token = jwt.create_reset_token(user.id, jti)

    try:
        await send_change_password_email(
            to=login.email, reset_token=reset_token.token
        )
    except Exception:
        logger.exception(
            "Failed to send change-password email"
        )
        await session.rollback()
        raise ApplicationException(f"Something went wrong!", 500)
    
    auth_audit.password_reset_requested(user.id, ip)

    await add_reset_jwt(session, user.id, reset_token.exp, jti, device)
    
    return {
        "message": "If an account with this email exists, password reset instructions have been sent."
    }


async def reset_user_password(session, token, password, ip):
    try:
        decoded = JWTService().decode_token(token)

        if decoded.token_type != "password_reset":
            raise ApplicationException(
                "Invalid token type", 401
            )
        
        existing_reset_token = await verify_reset_jwt(session, decoded.jti)

        if not existing_reset_token:
            raise ApplicationException("Reset token not found", 401)

        user_id = existing_reset_token.user_id
        user = await get_user_by_id(session, user_id)

        if not user.is_active:
            raise ApplicationException("User is inactive error", 403)

    except ResetTokenReuseDetection as e:
        auth_audit.token_reuse_detected(e.user_id, ip)

        await deactivate_all_user_reset_jwt(session, e.user_id)
        await deactivate_all_user_refresh(session, e.user_id)

        user = await get_user_by_id(session, e.user_id)

        try:
            await send_suspicios_login_attempt_caution(
                to=user.email,
                reason="изменение пароля"
            )
        except Exception:
            logger.exception(
                "Failed to send security email"
            )
        raise

    password_validity = check_password(password.password)
    if password_validity:
        raise ApplicationException(f"The password is weak: {password_validity}", 400)

    hashed_password = hash_password(password.password)

    await update_user_password(session, user, hashed_password)

    await deactivate_all_user_reset_jwt(session, user.id)
    await deactivate_all_user_refresh(session, user.id)

    auth_audit.password_reset_success(user_id, ip)

    return { 
        "message": "The password has been successfully updated!"
    }