from fastapi import HTTPException, APIRouter, Depends, Request
from .schemas import (
    Token,
    LoginRequest,
    SignupRequest,
    SignupResponse,
    RefreshRequest,
    LogoutResponse,
    ChangePasswordRequest,
    EmailResponse,
    ForgotLoginRequest,
    MessageResponse
)
from .service import (
    login_user,
    signup_user,
    update_tokens,
    logout_user,
    change_user_password,
    create_password_reset_token,
    reset_user_password
)
from .dependencies import get_allow_password_change_user, UserDTO
from app.config.config import ApplicationException
from app.config.connection import get_db
from app.database.refresh_token import TokenReuseDetection
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

auth_router = APIRouter()


@auth_router.post("/auth/login", response_model=Token)
async def login(
    input: LoginRequest, request: Request, session: AsyncSession = Depends(get_db)
):
    try:
        device = request.headers.get("user-agent")
        ip = request.client.host
        result = await login_user(session, input.email, input.password, device, ip)

        return {
            "access_token": result.access,
            "refresh_token": result.refresh,
            "token_type": "JWT",
            "change_password": result.change_password,
        }

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@auth_router.post("/auth/logout", response_model=LogoutResponse)
async def logout(input: RefreshRequest, session: AsyncSession = Depends(get_db)):
    try:
        return await logout_user(session, input.refresh_token)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} = {e}")


@auth_router.post("/auth/refresh", response_model=Token)
async def jwt_rotation(
    input: RefreshRequest,
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    try:
        device = request.headers.get("user-agent")
        token = await update_tokens(session, input.refresh_token, device)

        return {
            "access_token": token.access,
            "refresh_token": token.refresh,
            "token_type": "JWT",
            "change_password": False,
        }

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except TokenReuseDetection:
        raise HTTPException(status_code=401, detail="Session compromised")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error - {e}")


@auth_router.post("/auth/signup", response_model=SignupResponse)
async def signup(
    data_to_signup: SignupRequest,
    session: AsyncSession = Depends(get_db),
):
    try:
        return await signup_user(session, data_to_signup)

    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Integrity Error - {e}")

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error - {e}")


@auth_router.patch("/auth/change-password", response_model=EmailResponse)
async def change_password(
    new_data: ChangePasswordRequest,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(get_allow_password_change_user),
):
    try:
        email = await change_user_password(session, user.id, new_data.password)
        return {"email": email}

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@auth_router.post("/auth/forgot-password", response_model=MessageResponse)
async def forgot_password(
    login: ForgotLoginRequest,
    request: Request,
    session: AsyncSession = Depends(get_db),

):
    try:
        device = request.headers.get("user-agent")
        return await create_password_reset_token(session, login, device)

    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Integrity Error - {e}")

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error - {e}")


@auth_router.post("/auth/reset-password", response_model=MessageResponse)
async def reset_password(
    token: str,
    password: ChangePasswordRequest,
    session: AsyncSession = Depends(get_db),
):
    try:
        return await reset_user_password(session, token, password)

    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Integrity Error - {e}")

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error - {e}")
    

