from fastapi import APIRouter, Depends, HTTPException, Query, Form, Request
from fastapi.templating import Jinja2Templates
from app.auth.dependencies import require_page_roles, UserDTO
from app.config.config import ApplicationException
from app.config.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import require_roles, UserDTO
from dataclasses import dataclass
from app.services.email_log import get_email_log_list, get_email_log
from app.schemas.email_log import EmailLogList, EmailLogItem
from app.models.email_log import EmailLogStatus
from app.routers.email_log import ScopeEnum, EmailLogQueryDTO
from app.routers.user import QueryDTO
from app.services.user import get_user_list
from app.email.service import get_email_list


email_log_page_router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)


@email_log_page_router.get("/email-logs")
async def email_log_list_page(
    request: Request,
    scope: ScopeEnum | None = Query(default=None, description="scope=mine, in case roles include admin + other"),
    status: EmailLogStatus | None = Query(default=None),
    user_id: int | None = Query(default=None),
    to_email: str | None = Query(default=None),
    from_email: str | None = Query(default=None),
    sort: str | None = Query(default=None, description="- stands for desc"),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor"))
):
    context = {
        "request": request,
        "user": user,
        "email_logs": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
        "sort": sort,
        "status": status,
        "user_id": user_id,
        "to_email": to_email,
        "from_email": from_email,
        "scope": scope,
        "error": None,
    }

    try:
        query = EmailLogQueryDTO(
            sort=sort, limit=limit, 
            offset=offset, to_email=to_email, 
            user_id=user_id, scope=scope,
            from_email=from_email, status=status
        )
        result = await get_email_log_list(
            session=session, roles=user.roles, user_id=user.id, query=query
        )
        users_result = await get_user_list(
            session=session, roles=user.roles, query=QueryDTO(limit=1000)
        )
        emails_result = await get_email_list(
            session=session, 
            limit=1000, 
            offset=0, 
            user_id=user.id, 
            roles=user.roles, 
            scope=None
        )

        context.update(
            {
                "email_logs": result.get("items", []),
                "total": result.get("total", 0),
                "limit": result.get("limit", limit),
                "offset": result.get("offset", offset),
                "users": users_result.get("items", []),
                "emails": emails_result.get("items", [])
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="email_log/list.html",
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


@email_log_page_router.get("/email-logs/{email_logs_id}")
async def email_log_detail_page(
    request: Request,
    email_logs_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor")
    ),
):

    context = {
        "request": request,
        "user": user,
        "email_logs_id": email_logs_id,
        "error": None,
    }

    try:
        result = await get_email_log(session, user.roles, user.id, email_logs_id)

        context.update(
            {
                "status": result.status,
                "from_email": result.from_email,
                "to": result.to,
                "cc": result.cc,
                "bcc": result.bcc,
                "subject": result.subject,
                "body": result.body,
                "files_data": result.files_data,
                "created_at": result.created_at,
                "sent_at": result.sent_at,
                "error_message": result.error_message

            }
        )

        return templates.TemplateResponse(
            request=request,
            name="email_log/detail.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, name="error.html", 
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