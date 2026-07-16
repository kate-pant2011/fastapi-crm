from fastapi import APIRouter, Depends, HTTPException, Query
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import require_roles
from app.auth.dependencies import UserDTO
from app.config.connection import get_db
from app.schemas.common import BaseShortResponse, BaseListResponse
from app.schemas.project import ProjectItem
from app.schemas.stage_template import (
    StageTemplateItem,
    StageTemplateCreation,
    StageTemplatePatchRequest,
)
from app.services.stage_template import (
    get_stage_template_list,
    get_stage_template,
    create_stage_template,
    change_stage_template,
    create_stages_with_template,
)

stage_template_router = APIRouter()


@stage_template_router.get("/stage-templates", response_model=BaseListResponse)
async def get_stage_template_list_router(
    session: AsyncSession = Depends(get_db),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    creator_id: int | None = Query(default=None),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        return await get_stage_template_list(
            session=session, creator_id=creator_id, limit=limit, offset=offset
        )

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@stage_template_router.get("/stage-templates/{id}", response_model=StageTemplateItem)
async def get_stage_teplate_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        return await get_stage_template(session, id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@stage_template_router.post("/stage-templates", response_model=BaseShortResponse)
async def create_stage_template_router(
    data: StageTemplateCreation,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        return await create_stage_template(session, data, user.id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@stage_template_router.patch("/stage-templates/{id}", response_model=StageTemplateItem)
async def change_stage_template_router(
    data: StageTemplatePatchRequest,
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        return await change_stage_template(session, data, user.id, id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@stage_template_router.post(
    "/project/{project_id}/stage-templates/{stage_template_id}",
    response_model=ProjectItem,
)
async def create_stages_with_template_router(
    project_id: int,
    stage_template_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("manager")),
):
    try:
        return await create_stages_with_template(
            session, user.id, project_id, stage_template_id
        )

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")
