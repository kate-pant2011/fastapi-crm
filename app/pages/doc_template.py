from fastapi import APIRouter, Depends, HTTPException, Query, Form, Request
from fastapi.templating import Jinja2Templates
from app.auth.dependencies import require_page_roles, UserDTO
from typing import Literal
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.connection import get_db
from app.schemas.common import BaseShortResponse, BaseListResponse
from dataclasses import dataclass
from app.schemas.doc_template import (
    DocTemplateItem, 
    DocTemplateCreation, 
    DocTemplatePatchRequest, 
    DocTemplateDeleteResponse, 
    GeneratedDocResponse
)
from app.services.doc_template import (
    get_doc_template_list, 
    get_doc_template, 
    create_doc_template, 
    change_doc_template, 
    delete_doc_template, 
    render_doc_template,
)

doc_template_page_router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)

@doc_template_page_router.get("/doc-templates")
async def doc_template_list_page(
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
        "doc_templates": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
        "scope": scope,
        "error": None,
    }
    try:
        result = await get_doc_template_list(
            session=session, scope=scope, limit=limit, offset=offset, roles=user.roles, user_id=user.id
        )

        context.update(
            {
                "doc_templates": result.get("items", []),
                "total": result.get("total", 0),
                "limit": result.get("limit", limit),
                "offset": result.get("offset", offset),
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="doc_template/list.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, 
            name="doc_template/list.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="doc_template/list.html",
            context=context,
            status_code=500,
        )


@doc_template_page_router.get("/doc-templates/{doc_template_id}")
async def doc_template_detail_page(
    request: Request,
    doc_template_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor")
    ),
):

    context = {
        "request": request,
        "user": user,
        "doc_template_id": doc_template_id,
        "edit_url": f"/doc_templates/{doc_template_id}/edit",
        "delete_url": f"/doc_templates/{doc_template_id}/delete",
        "error": None,
    }

    try:
        result = await get_doc_template(session, doc_template_id, user.roles, user.id)

        context.update(
            {
                "name": result.name,
                "description": result.description,
                "is_public": result.is_public,
                "variables": result.variables,
                "creator": result.creator,
            }

        )
        return templates.TemplateResponse(
            request=request,
            name="doc_template/detail.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, name="doc_template/detail.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="doc_template/detail.html",
            context=context,
            status_code=500,
        )