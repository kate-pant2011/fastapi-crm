import jwt
from app.config.config import settings
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from dataclasses import dataclass
from typing import Set


@dataclass
class UserDTO:
    id: int
    roles: Set[str]


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def build_user_from_token(token: str, allow_password_change: bool = False) -> UserDTO:
    try:
        decoded = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    sub = decoded.get("sub")
    if not sub:
        raise HTTPException(status_code=404, detail="User Not Found")

    is_active = decoded.get("active")
    if not is_active:
        raise HTTPException(status_code=400, detail="User Not Active")

    must_change_password = decoded.get("status")

    if must_change_password and not allow_password_change:
        raise HTTPException(status_code=403, detail="Password change required")

    roles = set(decoded.get("roles", []))
    if not roles:
        raise HTTPException(status_code=403, detail="User Roles Not Assigned")

    return UserDTO(id=int(sub), roles=roles)


async def get_current_user(
        token: str = Depends(oauth2_scheme), allow_password_change=False
) -> UserDTO:
    return build_user_from_token(token, allow_password_change)


async def get_current_user_from_cookie(
        request: Request, allow_password_change=False
) -> UserDTO:
    token = getattr(
        request.state,
        "access_token",
        None,
    )

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
        )
    return build_user_from_token(token, allow_password_change)


def require_roles(*allowed_roles):
    def checker(user: UserDTO = Depends(get_current_user)):
        if not user.roles.intersection(allowed_roles):
            raise HTTPException(status_code=403, detail="Forbidden")
        return user

    return checker

def require_page_roles(*allowed_roles):
    def checker(user: UserDTO = Depends(get_current_user_from_cookie)):
        if not user.roles.intersection(allowed_roles):
            raise HTTPException(status_code=403, detail="Forbidden")
        return user

    return checker

async def get_allow_password_change_user(token: str = Depends(oauth2_scheme)):
    user = await get_current_user(token, allow_password_change=True)
    return user


async def get_allow_password_change_user_if_cookie(
    request: Request,
):
    return await get_current_user_from_cookie(
        request,
        allow_password_change=True,
    )