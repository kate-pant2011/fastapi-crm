from fastapi import APIRouter, Depends, HTTPException, Query
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import require_roles
from app.auth.dependencies import UserDTO
from app.config.connection import get_db
from app.schemas.base import ShortItem
from app.schemas.stage import (
    StageItem,
    StageCreation,
    StageTemplateItem,
    StageTemplateCreation
)
from app.services.stage import (
    get_stage_list,
    get_stage,
    create_stage,
    create_stage_template,
    archive_stage,
    restore_stage
)

stage_router = APIRouter()


@stage_router.get("/project/{project_id}/stage", response_model=list[ShortItem])
async def get_stage_list_router(
    project_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_roles("owner", "admin", "manager")
    ),
):
    try:
        return await get_stage_list(session, user.roles, user.id, project_id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@stage_router.get("/project/{project_id}/stage/{id}", response_model=StageItem)
async def get_stage_router(
    project_id: int,
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_roles("owner", "admin", "manager", "executor")
    ),
):
    try:
        return await get_stage(session, user.roles, user.id, project_id, id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@stage_router.post("/stage", response_model=ShortItem)
async def create_stage_router(
    data: StageCreation,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_roles("manager")
    ),
):
    try:
        return await create_stage(session, data, user.id)

    except ApplicationException as e:
        raise HTTPException(
            status_code=e.code, detail={"message": e.name, "payload": e.payload}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")
    
@stage_router.post("/stage-template", response_model=StageTemplateItem)
async def create_stage_template_router(
    data: StageTemplateCreation,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_roles("owner", "admin", "manager")
    )
):
    try:
        return await create_stage_template(session, data, user.id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")
    

@stage_router.delete("/project/{project_id}/stage/{id}", response_model=ShortItem)
async def archive_stage_router(
    project_id: int,
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_roles("manager")
    ),
):
    try:
        return await archive_stage(session, id, user.id, project_id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@stage_router.post("/project/{project_id}/stage/{id}/restore", response_model=ShortItem)
async def restore_stage_router(
    project_id: int,
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_roles("owner", "admin", "manager")
    ),
):
    try:
        return await restore_stage(session, id, user.roles,  user.id, project_id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")