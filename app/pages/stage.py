from fastapi import APIRouter, Depends, HTTPException, Query, Form, Request
from fastapi.templating import Jinja2Templates
from app.auth.dependencies import require_page_roles, UserDTO
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.connection import get_db
from dataclasses import dataclass
from app.schemas.common import BaseShortResponse, BaseListResponse
from app.schemas.stage import (
    StageItem,
    StageCreation,
    StagePatchRequest,
    StageReorderRequest,
    ReorderResultResponse
)
from app.services.stage import (
    get_stage_list,
    get_stage,
    create_stage,
    archive_stage,
    restore_stage,
    change_stage,
    reorder_stages,
)
from app.routers.stage import StageQueryDTO

stage_page_router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)


@stage_page_router.patch(
    "/projects/{project_id}/stages/reorder", response_model=ReorderResultResponse
)
async def reorder_stages_router(
    request: Request,
    item: StageReorderRequest,
    project_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_page_roles("owner", "admin", "manager")),
):
    context = {
        "request": request,
        "user": user,
        "error": None,
    }
    try:
        await reorder_stages(
            session,
            user.roles,
            user.id,
            project_id,
            item
        )

        return {
            "result": "success"
        }
    
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


@stage_page_router.get("/projects/{project_id}/stages/{stage_id}")
async def stage_detail_page(
    request: Request,
    project_id: int,
    stage_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor")
    ),
):

    context = {
        "request": request,
        "user": user,
        "stage_id": stage_id,
        "edit_url": f"/projects/{project_id}/stages/{stage_id}/edit",
        "delete_url": f"/projects/{project_id}/stages/{stage_id}/delete",
        "restore_url": f"/projects/{project_id}/stages/{stage_id}/restore",
        "email_url":f"/email-templates?stage_id={stage_id}&project_id={project_id}", 
        "document_url":f"/doc-templates?stage_id={stage_id}", 
        "return_url": f"/projects/{project_id}", 
        "error": None,
    }

    try:
        result = await get_stage(session, user.roles, user.id, project_id, stage_id)

        context.update(
            {
                "name": result.name,
                "position": result.position,
                "description": result.description,
                "start_date": result.start_date,
                "end_date": result.end_date,
                "project": result.project,
                "assignments": result.assignments,
                "is_archived": result.is_archived,
            }
        )

        return templates.TemplateResponse(
            request=request,
            name="stage/detail.html",
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


@stage_page_router.post("/projects/{project_id}/stages/{stage_id}/delete")
async def stage_delete_page(
    request: Request,
    project_id: int,
    stage_id: int, 
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("manager")
    ),
):

    context = {
        "request": request,
        "user": user,
        "project_id": project_id, 
        "stage_id": stage_id,
        "detail_url": f"/projects/{project_id}/stages/{stage_id}",
        "error": None,
        "return_url": f"/projects/{project_id}", 
    }

    try:
        result = await archive_stage(session, stage_id, user.id, project_id)

        context.update(
            {
                "name": result.name,
                "message": "удаление", 
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


@stage_page_router.post("/projects/{project_id}/stages/{stage_id}/restore")
async def stage_restore_page(
    request: Request,
    project_id: int,
    stage_id: int, 
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager")
    ),
):

    context = {
        "request": request,
        "user": user,
        "project_id": project_id, 
        "stage_id": stage_id,
        "detail_url": f"/projects/{project_id}/stages/{stage_id}",
        "return_url": f"/projects/{project_id}", 
        "error": None,
    }

    try:
        result = await restore_stage(session, stage_id, user.roles, user.id, project_id)

        context.update(
            {
                "name": result.name,
                "message": "восстановление",
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