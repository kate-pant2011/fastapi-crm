from fastapi import APIRouter, Depends, HTTPException, Query, Form, Request
from fastapi.templating import Jinja2Templates
from app.auth.dependencies import require_page_roles, UserDTO
from typing import Literal
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.connection import get_db
from app.schemas.common import BaseShortResponse, BaseListResponse
from dataclasses import dataclass
from app.schemas.email_template import (
    EmailTemplateItem, 
    EmailTemplateCreation, 
    EmailTemplatePatchRequest, 
    EmailTemplateDeleteResponse, 
    EmailTemplateShortItem,
)
from app.services.email_template import (
    get_email_template_list, 
    get_email_template, 
    create_email_template, 
    change_email_template, 
    delete_email_template, 
    render_email_template,
)
from app.services.stage_template import get_stage_template_list

email_template_page_router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)

@email_template_page_router.get("/email-templates")
async def email_template_list_page(
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
        "email_templates": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
        "scope": scope,
        "error": None,
    }
    try:
        result = await get_email_template_list(
            session=session, scope=scope, limit=limit, offset=offset, roles=user.roles, user_id=user.id
        )

        context.update(
            {
                "email_templates": result.get("items", []),
                "total": result.get("total", 0),
                "limit": result.get("limit", limit),
                "offset": result.get("offset", offset),
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="email_template/list.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, 
            name="email_template/list.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="email_template/list.html",
            context=context,
            status_code=500,
        )


@email_template_page_router.get("/email-templates/{email_template_id}")
async def email_template_detail_page(
    request: Request,
    email_template_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor")
    ),
):

    context = {
        "request": request,
        "user": user,
        "email_template_id": email_template_id,
        "edit_url": f"/email_templates/{email_template_id}/edit",
        "delete_url": f"/email_templates/{email_template_id}/delete",
        "error": None,
    }

    try:
        result = await get_email_template(session, email_template_id, user.roles, user.id)

        context.update(
            {
                "name": result.name,
                "subject_content": result.subject_content,
                "body_content": result.body_content,
                "is_public": result.is_public,
                "creator": result.creator
            }
        )

        return templates.TemplateResponse(
            request=request,
            name="email_template/detail.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, name="email_template/detail.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="email_template/detail.html",
            context=context,
            status_code=500,
        )