from fastapi import APIRouter, Depends, HTTPException, Query, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.auth.dependencies import require_page_roles, UserDTO
from fastapi.responses import RedirectResponse
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.connection import get_db
from app.schemas.common import BaseShortResponse, BaseListResponse
from app.schemas.project import ProjectItem
from app.schemas.stage_template import StageTemplateCreation, StageTemplatePatchRequest
from app.services.stage_template import (
    get_stage_template_list,
    get_stage_template,
    create_stage_template,
    change_stage_template,
    create_stages_with_template,
)
from app.services.stage_template import get_all_stage_templates
from app.routers.user import QueryDTO
from app.routers.stage import StageQueryDTO
from app.services.stage import get_stage_list
from app.services.user import get_user_list
from .common import preparing_list_for_db


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


@stage_template_page_router.get("/stage-templates/create")
async def create_stage_template_page_(
    request: Request,
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager")
    ),
):
    context = {
        "request": request,
        "user": user,
        "create_url": "/stage-templates/create",
    }

    return templates.TemplateResponse(
        request=request,
        name="stage_template/create.html",
        context=context,
    )


@stage_template_page_router.post("/stage-templates/create")
async def create_stage_template_page(
    request: Request,
    name: str = Form(...),
    stage_list: str = Form(...),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_page_roles("owner", "admin", "manager")),
):
    context = {
        "request": request,
        "user": user,
        "create_url": "/stage-templates/create",
        "return_url": "/stage-templates",
        "error": None,
    }

    if stage_list:
        if stage_list[-1] == ",":
            context["error"] = "Нельзя заканчивать список запятой"
            return templates.TemplateResponse(
                request=request, 
                name="error.html", 
                context=context,
                status_code=400,
            )
        elif "," in stage_list:
            stage_list = stage_list.split(",")
        else:
            stage_list = [stage_list]

    try:
        data = StageTemplateCreation(
            name=name,
            stage_list=stage_list,
        )

        result = await create_stage_template(session, data, user.id)

        context.update(
            {
                "id": result.id,
                "name": result.name,
                "form_data": {
                    "name": name,
                    "stage_list": stage_list,
                }
            }
        )

        return templates.TemplateResponse(
            request=request,
            name="archived_restored.html",
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
        "edit_url": f"/stage-templates/{stage_template_id}/edit",
        "delete_url": f"/stage-templates/{stage_template_id}/delete",
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


@stage_template_page_router.get("/stage-templates/{id}/edit")
async def edit_stage_template_page(
    request: Request,
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles(
            "owner", "admin", "manager",
        )
    ),
):
    context = {
        "request": request,
        "user": user,
        "edit_url": f"/stage-templates/{id}/edit",
        "error": None,
        "return_url": "/stage-templates",
    }

    try:
        result = await get_stage_template(session, id)

        context["template"] = result

        return templates.TemplateResponse(
            request=request,
            name="stage_template/edit.html",
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


@stage_template_page_router.post("/stage-templates/{id}/edit")
async def stage_doc_template(
    request: Request,
    id: int,
    stage_list: str | None = Form(None),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles(
            "owner", "admin", "manager",
        )
    ),
):
    context = {
        "request": request,
        "user": user,
        "edit_url": f"/stage-templates/{id}/edit",
        "return_url": "/stage-templates",
        "error": None,
    }

    if stage_list:
        if stage_list[-1] == ",":
            context["error"] = "Нельзя заканчивать список запятой"
            return templates.TemplateResponse(
                request=request, 
                name="error.html", 
                context=context,
                status_code=400,
            )
        elif "," in stage_list:
            stage_list = stage_list.split(",")
        else:
            stage_list = [stage_list]
        
    try:
        data = StageTemplatePatchRequest(
            stage_list=stage_list,
        )

        result = await change_stage_template(
            session=session,
            data=data,
            user_id=user.id,
            id=id,
        )

        context["template"] = result

        return RedirectResponse(
            url=f"/stage-templates/{id}",
            status_code=303,
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


@stage_template_page_router.post("/projects/{project_id}/stage-template")
async def create_stage_page_(
    request: Request,
    project_id: int,
    stage_template_id: int = Form(...),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("manager")
    ),
):
    context = {
        "request": request,
        "user": user,
        "create_url": f"/projects/{project_id}/stage-template",
        "return_url": f"/projects",
        "project_id": project_id,
        "stage_template_id": stage_template_id,
        "error": None,
    }
    try:

        result = await create_stages_with_template(
            session, user.id, project_id, stage_template_id
        )

        return RedirectResponse(
            url=f"/projects/{project_id}#stages",
            status_code=303,    
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