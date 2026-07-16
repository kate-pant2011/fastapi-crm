from fastapi import HTTPException, APIRouter, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
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
from .dependencies import get_allow_password_change_user_if_cookie, UserDTO
from app.config.config import ApplicationException
from app.config.connection import get_db
from app.database.refresh_token import TokenReuseDetection
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.rate_limit import limiter

auth_page_router = APIRouter(prefix="/auth")

templates = Jinja2Templates(
    directory="app/templates"
)

@auth_page_router.get("/")
async def auth_index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth/index.html"
    )


@auth_page_router.get("/signup")
async def signup_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth/signup.html"
    )


@auth_page_router.post("/signup-page")
@limiter.limit("3/minute")
async def signup_page_submit(
    request: Request,
    session: AsyncSession = Depends(get_db),
    inn: str = Form(...),
    company: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    surname: str = Form(...),
    position: str = Form(...),
):
    try:
        signup_data = SignupRequest(
            inn=inn,
            company=company,
            email=email,
            password=password,
            name=name,
            surname=surname,
            position=position,
        )

        ip = request.client.host

        result = await signup_user(session, signup_data, ip)

        response = RedirectResponse(
            url=f"/auth/login?login={result.login}",
            status_code=303,
        )

        return response

    except IntegrityError as e:
        print("IntegrityError")
        error = f"Integrity Error - {e}"
        return templates.TemplateResponse(
            request=request, name="auth/signup.html", context={"error": error},
            status_code=400,
    )

    except ApplicationException as e:
        print("APPLICATION EXCEPTION")
        return templates.TemplateResponse(
            request=request, name="auth/signup.html", context={"error": e.name},
            status_code=e.code,
    )

    except Exception as e:
        error = f"Internal server error - {e}"
        print("EXCEPTION")
        return templates.TemplateResponse(
            request=request, name="auth/signup.html", context={
                "error": error
            },
            status_code=500,
    )
    

@auth_page_router.get("/login")
async def login_page(
    request: Request,
    login: str | None = None,
):
    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={
            "login": login,
        },
    )


@auth_page_router.post("/login-page")
@limiter.limit("3/minute")
async def login_page_submit(
    request: Request,
    session: AsyncSession = Depends(get_db),
    email: str = Form(...),
    password: str = Form(...),
):
    try:
        device = request.headers.get("user-agent")
        ip = request.client.host

        result = await login_user(
            session=session,
            email=email,
            password=password,
            device=device,
            ip=ip,
        )

        if result.change_password:
            response = RedirectResponse(
                url="/auth/change-password",
                status_code=303,
            )
        else:
            response = RedirectResponse(url="/", status_code=303)

        response.set_cookie(
            key="access_token",
            value=result.access,
            httponly=True,
            samesite="lax",
            secure=False,  # True на проде
        )

        if result.refresh:
            response.set_cookie(
                key="refresh_token",
                value=result.refresh,
                httponly=True,
                samesite="lax",
                secure=False,
            )
        return response

    except ApplicationException as e:

        return templates.TemplateResponse(
            request=request, name="auth/login.html", context={
                "error": e.name,
                "email": email,
            },
            status_code=e.code,
        )

    except Exception as e:

        return templates.TemplateResponse(
            request=request, name="auth/login.html",context={
                "error": f"{type(e).__name__} - {e}",
                "email": email,
            },
            status_code=500,
        )


@auth_page_router.post("/logout-page")
async def logout_page(
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    try:
        refresh_token = request.cookies.get("refresh_token")
        if refresh_token:
            await logout_user(session,refresh_token)

        response = RedirectResponse(
            url="/auth",
            status_code=303,
        )
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response

    except ApplicationException as e:
        response = RedirectResponse(
            url="/auth",
            status_code=303,
        )
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response

    except Exception:
        response = RedirectResponse(
            url="/auth",
            status_code=303,
        )
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response
    

@auth_page_router.get("/forgot-password")
async def forgot_password_page(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="auth/forgot_password.html",
    )

@auth_page_router.post("/forgot-password-page")
@limiter.limit("1/minute")
async def forgot_password_submit(
    request: Request,
    session: AsyncSession = Depends(get_db),

    email: str = Form(...),
):
    try:
        device = request.headers.get("user-agent")
        ip = request.client.host

        result = await create_password_reset_token(
            session,
            ForgotLoginRequest(email=email),
            device,
            ip,
        )
        return templates.TemplateResponse(
            request=request,
            name="auth/forgot_password.html",
            context={
                "success": result.get("message"),
            },
        )
    except IntegrityError as e:
        return templates.TemplateResponse(
            request=request,
            name="auth/forgot_password.html",
            context={"error": f"Integrity Error - {e}"},
            status_code=400,
        )

    except ApplicationException as e:
        return templates.TemplateResponse(
            request=request,
            name="auth/forgot_password.html",
            context={"error": e.name},
            status_code=e.code,
        )

    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="auth/forgot_password.html",
            context={"error": f"Internal server error - {e}"},
            status_code=500,
        )
    
@auth_page_router.get("/reset-password")
async def reset_password_page(
    request: Request,
    token: str,
):
    return templates.TemplateResponse(
        request=request,
        name="auth/reset_password.html",
        context={
            "token": token,
        },
    )

@auth_page_router.post("/reset-password-page")
@limiter.limit("5/minute")
async def reset_password_submit(
    request: Request,
    session: AsyncSession = Depends(get_db),

    token: str = Form(...),
    password: str = Form(...),
):
    try:
        ip = request.client.host
        result = await reset_user_password(
            session,
            token, 
            ChangePasswordRequest(password=password),
            ip,
        )

        return RedirectResponse(
            url="/auth/login",
            status_code=303,
        )
    except IntegrityError as e:
        return templates.TemplateResponse(
            request=request,
            name="auth/reset_password.html",
            context={
                "token": token,
                "error": f"Integrity Error - {e}",
            },
            status_code=400,
        )

    except ApplicationException as e:
        return templates.TemplateResponse(
            request=request,
            name="auth/reset_password.html",
            context={
                "token": token,
                "error": e.name,
            },
            status_code=e.code,
        )

    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="auth/reset_password.html",
            context={
                "token": token,
                "error": f"Internal server error - {e}",
            },
            status_code=500,
        )
    

@auth_page_router.get("/change-password")
async def change_password_page(
    request: Request,
    user: UserDTO = Depends(
        get_allow_password_change_user_if_cookie
    ),
):
    return templates.TemplateResponse(
        request=request,
        name="auth/change_password.html",
    )


@auth_page_router.post("/change-password-page")
async def change_password_submit(
    request: Request,
    session: AsyncSession = Depends(get_db),
    password: str = Form(...),
    user: UserDTO = Depends(get_allow_password_change_user_if_cookie),
):
    try:
        ip = request.client.host
        await change_user_password(session, user.id, password, ip)

        response = RedirectResponse(
            url="/auth/login",
            status_code=303,
        )
        response.delete_cookie("access_token")
        return response

    except ApplicationException as e:
        return templates.TemplateResponse(
            request=request,
            name="auth/change_password.html",
            context={"error": e.name},
            status_code=e.code,
        )

    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="auth/forgot_password.html",
            context={"error": f"Internal server error - {e}"},
            status_code=500,
        )