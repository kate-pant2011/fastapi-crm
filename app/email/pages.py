from fastapi import APIRouter, Depends, HTTPException, Query, Form, Request, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.auth.dependencies import require_page_roles, UserDTO
from typing import Literal
from app.config.config import ApplicationException
from app.config.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from .service import add_email_user, send_email_service, get_email_list, get_email, change_email, delete_email, validate_fastapi_file
from .schemas import (
    EmailShortResponse, EmailPostRequest, EmailStatusResponse, EmailListResponse, EmailItem, EmailPatchRequest
)
from app.services.user import get_user_list
from app.routers.user import QueryDTO

email_page_router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)

@email_page_router.get("/email-accounts")
async def email_list_page(
    request: Request,
    scope: Literal["mine", "available"] | None = Query(
        default=None, 
        description="Filter: mine (only personal), available (shared + personal)"
    ),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor"))
):
    context = {
        "request": request,
        "user": user,
        "user_roles": user.roles,
        "emails": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
        "scope": scope,
        "error": None,
    }
    try:
        result = await get_email_list(
            session, limit, offset, user.id, user.roles, scope
        )

        context.update(
            {
                "emails": result.get("items", []),
                "total": result.get("total", 0),
                "limit": result.get("limit", limit),
                "offset": result.get("offset", offset),
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="email/list.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, 
            name="email/list.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="email/list.html",
            context=context,
            status_code=500,
        )


@email_page_router.get("/email-accounts/create")
async def create_email_page_(
    request: Request,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin")
    ),
):

    try:
        query = QueryDTO(
            limit=1000,
            offset=0,
        )
        result = await get_user_list(session=session, roles=user.roles, query=query)
        context = {
            "users": result.get("items", []),
            "request": request,
            "user": user,
            "create_url": "/email-accounts/create",
        }

        return templates.TemplateResponse(
            request=request,
            name="email/create.html",
            context=context,
        )
    except ApplicationException as e:
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, 
            name="error.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="error.html",
            context=context,
            status_code=500,
        )


@email_page_router.post("/email-accounts/create")
async def create_email_page(
    request: Request,
    login: str = Form(...), 
    password: str = Form(...),
    server: str = Form(None),
    port: int = Form(None),
    assigned_user_id: int = Form(None),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_page_roles("owner", "admin")),
):
    context = {
        "request": request,
        "user": user,
        "create_url": "/email-accounts/create",
        "return_url": "/email-accounts",
        "error": None,
    }

    try:
        query = QueryDTO(
            is_active=True,
            limit=1000,
            offset=0,
        )
        result = await get_user_list(session=session, roles=user.roles, query=query)
        context.update({"users": result.get("items", [])})
        data = EmailPostRequest(
            login=login, 
            password=password,
            server=server,
            port=port,
            assigned_user_id=assigned_user_id,
        )

        result = await add_email_user(session, data, user.id)

        context.update(
            {
                "id": result.id,
                "login": result.login,
                "form_data": {
                    "login": login,
                    "password": password,
                    "server": server,
                    "port": port,
                    "assigned_user_id": assigned_user_id
                }
            }
        )

        return templates.TemplateResponse(
            request=request,
            name="archived_restored.html",
            context=context,
        )

    except ApplicationException as e:
        await session.rollback()
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, 
            name="error.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        await session.rollback()
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="error.html",
            context=context,
            status_code=500,
        )

    
@email_page_router.get("/email-accounts/{email_id}")
async def email_detail_page(
    request: Request,
    email_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin")
    ),
):

    context = {
        "request": request,
        "user": user,
        "email_account_id": email_id,
        "edit_url": f"/email-accounts/{email_id}/edit",
        "delete_url": f"/email-accounts/{email_id}/delete",
        "error": None,
    }

    try:
        result = await get_email(session, email_id)

        context.update(
            {
                "email_id": result.id,
                "login": result.login,
                "server": result.server,
                "port": result.port,
                "owner_id": result.owner_id,
                "creator_id": result.creator_id
            }
        )

        return templates.TemplateResponse(
            request=request,
            name="email/detail.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, name="email/detail.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="email/detail.html",
            context=context,
            status_code=500,
        )


@email_page_router.post("/email-accounts/{email_id}/delete")
async def email_delete_page(
    request: Request,
    email_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin")
    ),
):

    context = {
        "request": request,
        "user": user,
        "email__id": email_id,
        "detail_url": f"/email-accounts/{email_id}",
        "error": None,
    } 

    try:
        await delete_email(session, email_id, user.id, user.roles)

        context.update(
            {
                "name": "Аккаунт почты",
                "deleted": "Удален без возможности восстановления",
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="archived_restored.html",
            context=context,
        )

    except ApplicationException as e:
        await session.rollback()
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, name="error.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        await session.rollback()
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="error.html",
            context=context,
            status_code=500,
        )


@email_page_router.post("/email/send", response_model=EmailStatusResponse)
async def send_email_page(
    request: Request,
    generated_id: int | None = Query(default=None),
    files: list[UploadFile] | None = File(None),
    email_id: int = Form(...),
    to: str = Form(...),
    cc: str = Form(None),
    bcc: str = Form(None),
    subject: str = Form(None),
    body: str = Form(None),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_page_roles("owner", "admin", "manager", "executor")),
):
    context = {
        "request": request,
        "user": user,
        "email__id": email_id,
        "error": None,
    } 
    try: 
        validated_files = await validate_fastapi_file(files)

        result = await send_email_service(
            session, 
            validated_files,
            email_id,
            to,
            cc,
            bcc,
            subject,
            body,
            user.id,
            generated_id
        )

        return RedirectResponse(
            "/email-logs",
            status_code=303,
        )

    except ApplicationException as e:
        await session.rollback()
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, name="error.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        await session.rollback()
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="error.html",
            context=context,
            status_code=500,
        )


@email_page_router.get("/email-accounts/{id}/edit")
async def email_contractor_page(
    request: Request,
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles(
            "owner", "admin",
        )
    ),
):
    context = {
        "request": request,
        "user": user,
        "edit_url": f"/email-accounts/{id}/edit",
        "error": None,
        "return_url": "/email-accounts",
    }

    try:
        result = await get_email(session, id)

        context["template"] = result

        query = QueryDTO(
            limit=1000,
            offset=0,
        )
        users = await get_user_list(session=session, roles=user.roles, query=query)
        context["users"] = users.get("items", [])

        return templates.TemplateResponse(
            request=request,
            name="email/edit.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__}: {e}"

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context=context,
            status_code=500,
        )


@email_page_router.post("/email-accounts/{id}/edit")
async def contractor_template(
    request: Request,
    id: int,
    login: str = Form(None), 
    password: str = Form(None),
    server: str = Form(None),
    port: int = Form(None),
    owner_id: int = Form(None),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles(
            "owner", "admin", 
        )
    ),
):
    context = {
        "request": request,
        "user": user,
        "edit_url": f"/email-accounts/{id}/edit",
        "return_url": "/email-accounts",
        "error": None,
    }
        
    try:
        data = {
            "login": login,
            "server": server,
            "port": port,
            "owner_id": owner_id,
        }

        if password:
            data["password"] = password

        item = EmailPatchRequest(**data)   

        result = await change_email(session, item, id, user.id)

        context["template"] = result

        return RedirectResponse(
            url=f"/email-accounts/{id}",
            status_code=303,
        )

    except ApplicationException as e:
        await session.rollback()
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        await session.rollback()
        context["error"] = f"{type(e).__name__}: {e}"

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context=context,
            status_code=500,
        )