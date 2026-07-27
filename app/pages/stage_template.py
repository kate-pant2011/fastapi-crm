from fastapi import APIRouter, Depends, HTTPException, Query, Form, Request
from fastapi.templating import Jinja2Templates
from app.auth.dependencies import require_page_roles, UserDTO
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.connection import get_db
from app.schemas.common import BaseShortResponse, BaseListResponse
from app.schemas.project import ProjectItem
from app.services.stage_template import (
    get_stage_template_list,
    get_stage_template,
)
from app.services.stage_template import get_all_stage_templates
from app.routers.user import QueryDTO
from app.services.user import get_user_list


stage_template_page_router = APIRouter()


templates = Jinja2Templates(
    directory="app/templates"
)

@stage_template_page_router.get("/stage-templates")
async def stage_template_list_page(
    request: Request,
    creator_id: int | None = Query(default=None),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager"))
):
    context = {
        "request": request,
        "user": user,
        "stage_templates": [],
        "creators": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
        "creator_id": creator_id,
        "error": None,
    }
    try:
        result = await get_stage_template_list(
            session=session, creator_id=creator_id, limit=limit, offset=offset
        )

        creators_result = await get_user_list(
            session=session, roles=user.roles, query=QueryDTO(limit=1000)
        )

        context.update(
            {
                "stage_templates": result.get("items", []),
                "total": result.get("total", 0),
                "limit": result.get("limit", limit),
                "offset": result.get("offset", offset),
                "creators": creators_result.get("items", [])
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="stage_template/list.html",
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


@stage_template_page_router.get("/stage-templates/{stage_template_id}")
async def stage_template_detail_page(
    request: Request,
    stage_template_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager")
    ),
):

    context = {
        "request": request,
        "user": user,
        "stage_template_id": stage_template_id,
        "edit_url": f"/stage_templates/{stage_template_id}/edit",
        "delete_url": f"/stage_templates/{stage_template_id}/delete",
        "return_url": "/stage-templates",
        "error": None,
    }

    try:
        result = await get_stage_template(session, stage_template_id)

        context.update(
            {
                "name": result.name,
                "stage_list": result.stage_list,
                "creator": result.creator,
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="stage_template/detail.html",
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