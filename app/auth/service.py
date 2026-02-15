# business logic
from app.config.security import verify_password, hash_password, check_password, JWTService
from app.database.repositories.branch import get_company_by_inn, create_company
from app.database.repositories.user import get_user_by_email, create_user, add_user_role, get_user_by_id
from app.database.repositories.refresh_token import add_refresh_jwt, verify_refresh_jwt, get_refresh_by_jwt, deactivate_user_refresh, deactivate_all_user_refresh
from app.database.repositories.refresh_token import TokenReuseDetection
from sqlalchemy.exc import IntegrityError
import uuid
from dataclasses import dataclass

@dataclass
class AuthTokensDTO:
  access: str
  refresh: str

class InvalidPasswordError(Exception):
    pass

class UserAlreadyExistsError(Exception):
    pass

class CompanyAlreadyExistsError(Exception):
    pass

class InvalidCredentialsError(Exception):
    pass

class UserIsInactiveError(Exception):
    pass

async def logout_user(session, refresh_jwt):
    try:
        decoded = JWTService().decode_token(refresh_jwt)
        refresh = await get_refresh_by_jwt(session, decoded.jti)

        await deactivate_user_refresh(session, refresh.user_id, refresh.jti) 
        await session.commit()      

    except IntegrityError:
        await session.rollback()
        raise

    return {"result": True} 

async def login_user(session, email, password, device):
    user = await get_user_by_email(session, email)
    if not user:
        raise InvalidCredentialsError(f"User {email} Not Found")

    if not verify_password(password, user.password_hash):
        raise InvalidCredentialsError("invalid password")
    
    roles = [role.name for role in user.roles]

    jti = str(uuid.uuid4())

    jwt = JWTService()
    access_token = jwt.create_access(user.id, roles)
    refresh = jwt.create_refresh(user.id, jti)
    exp = refresh.exp

    try:
        await add_refresh_jwt(session, user.id, exp, jti, device)
        await session.commit()

    except IntegrityError:
        await session.rollback()
        raise UserIsInactiveError

    return AuthTokensDTO(
      access=access_token,
      refresh=refresh.token
    )

async def update_tokens(session, refresh_jwt, device):
    try:
        decoded = JWTService().decode_token(refresh_jwt)
        old_refresh = await verify_refresh_jwt(session, decoded.jti)

        user_id = old_refresh.user_id
        user = await get_user_by_id(session, user_id)

        if not user.is_active:
            raise UserIsInactiveError

        roles = [role.name for role in user.roles]  
    
    except IntegrityError:
        await session.rollback()
        raise

    except TokenReuseDetection as e:
        await session.rollback()
        await deactivate_all_user_refresh(session, e.user_id)
        await session.commit()
        raise 

    jti = str(uuid.uuid4())

    jwt = JWTService()
    access_token = jwt.create_access(user_id, roles)
    refresh = jwt.create_refresh(user_id, jti)

    try:
        await add_refresh_jwt(session, user_id, refresh.exp, jti, device)
        await session.commit()

    except IntegrityError:
        await session.rollback()
        raise

    return AuthTokensDTO(
      access=access_token,
      refresh=refresh.token
    )


async def verify_inn(session, inn: int) -> dict:
    company = await get_company_by_inn(session, inn)
    if company:
        raise CompanyAlreadyExistsError(f"A company with INN '{inn}' already exists")

    return {
        "inn": inn,
        "can_signup": True,
        "company": None,
        "reason": None
    }

    
async def signup_user(db, inn, company, login, password, name, surname, position) -> dict:
    user_exists = await get_user_by_email(db, login)
    if user_exists:
        raise UserAlreadyExistsError(f"Email {login} is already used")

    password_invalid = check_password(password)
    if password_invalid:
        raise InvalidPasswordError(password_invalid)

    try:
        new_company = await create_company(db, inn, company)
        hashed_password = hash_password(password)
        new_user = await create_user(db, login, hashed_password, name, surname, position, new_company)
        await add_user_role(db, new_user)
        await db.commit()

    except IntegrityError:
        await db.rollback()
        raise

    return {
        "company": company,
        "login": login,
        "reason": None
    }

