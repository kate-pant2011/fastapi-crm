from fastapi import HTTPException, APIRouter, Depends, Request
from .schemas import LoginRequest, Token, InnResponse, InnRequest, SignupRequest, SignupResponse, RefreshRequest, LogoutResponse
from .service import login_user, verify_inn, signup_user, update_tokens, logout_user
from .service import InvalidPasswordError, UserAlreadyExistsError, CompanyAlreadyExistsError
from .service import InvalidCredentialsError, UserIsInactiveError
from app.database.repositories.refresh_token import TokenReuseDetection, RefreshTokenNotFound
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from sqlalchemy.exc import IntegrityError


auth_router = APIRouter()

@auth_router.post("/auth/logout", response_model=LogoutResponse)
async def logout(input: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await logout_user(db, input.refresh_token)

    except RefreshTokenNotFound:
        raise HTTPException(status_code=401, detail="Refresh token not found")   
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} = {e}")

@auth_router.post("/auth/login", response_model=Token)
async def login(input: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    try:
        device = request.headers.get("user-agent")
        token = await login_user(db, input.email, input.password, device)
  
        return {
            "access_token": token.access, 
            "refresh_token": token.refresh, 
            "token_type": "JWT"
        }
    
    except InvalidCredentialsError:
        raise HTTPException(status_code=401,detail="Invalid credentials")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")

@auth_router.post("/auth/refresh", response_model=Token)
async def jwt_rotation(
    input: RefreshRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    try:
        device = request.headers.get("user-agent")
        token = await update_tokens(db, input.refresh_token, device)

        return {
            "access_token": token.access, 
            "refresh_token": token.refresh, 
            "token_type": "JWT"
        } 
    
    except UserIsInactiveError:
        raise HTTPException(status_code=403, detail="Inactive user")

    except RefreshTokenNotFound:
        raise HTTPException(status_code=401, detail="Refresh token not found")
    
    except TokenReuseDetection:
        raise HTTPException(status_code=401, detail="Session compromised")    
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error - {e}")  
    
@auth_router.post("/auth/check-inn", response_model=InnResponse)
async def check_inn(
    input: InnRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await verify_inn(db, input.inn)
    
    except CompanyAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error - {e}")


@auth_router.post("/auth/signup", response_model=SignupResponse)
async def signup(
    input: SignupRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await signup_user(
            db, input.inn,
            input.company, 
            input.login, 
            input.password,
            input.name,
            input.surname,
            input.position
        )
    except IntegrityError as e:
        raise HTTPException(status_code=409,detail=f"Integrity Error - {e}")
    
    except InvalidPasswordError as e:
        raise HTTPException(status_code=422, detail=f"The password {e}")
    
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error - {e}")


  