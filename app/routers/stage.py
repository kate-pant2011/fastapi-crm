from fastapi import APIRouter, Depends, HTTPException, Query
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import require_roles
from app.auth.dependencies import UserDTO
from app.config.connection import get_db
from dataclasses import dataclass
from app.schemas.common import BaseShortResponse, BaseListResponse
from app.schemas.stage import (
    StageItem,
    StageCreation,
    StagePatchRequest,
    StageReorderRequest,
    StageListResponse
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

stage_router = APIRouter()


@dataclass
class StageQueryDTO:
    sort: str | None = None
    limit: int = 20
    offset: int = 0


@stage_router.get("/project/{project_id}/stages", response_model=StageListResponse)
async def get_stage_list_router(
    project_id: int,
    sort: str | None = Query(default=None, description="- stands for desc"),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        query = StageQueryDTO(sort=sort, limit=limit, offset=offset)
        return await get_stage_list(session, user.roles, user.id, project_id, query)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@stage_router.get("/project/{project_id}/stages/{id}", response_model=StageItem)
async def get_stage_router(
    project_id: int,
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        return await get_stage(session, user.roles, user.id, project_id, id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail={"message": e.name, "payload": e.payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@stage_router.patch("/project/{project_id}/stages/{stage_id}", response_model=StageItem)
async def change_stage_router(
    project_id: int,
    stage_id: int,
    item: StagePatchRequest,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        return await change_stage(
            session, user.roles, user.id, project_id, stage_id, item
        )

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail={"message": e.name, "payload": e.payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@stage_router.patch(
    "/project/{project_id}/stages/reorder", response_model=list[BaseShortResponse]
)
async def reorder_stages_router(
    item: StageReorderRequest,
    project_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        return await reorder_stages(session, user.roles, user.id, project_id, item)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail={"message": e.name, "payload": e.payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@stage_router.post("/stage", response_model=BaseShortResponse)
async def create_stage_router(
    data: StageCreation,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("manager")),
):
    try:
        return await create_stage(session, data, user.id)

    except ApplicationException as e:
        raise HTTPException(
            status_code=e.code, detail={"message": e.name, "payload": {"message": e.name, "payload": e.payload}}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@stage_router.delete(
    "/project/{project_id}/stages/{stage_id}", response_model=BaseShortResponse
)
async def archive_stage_router(
    project_id: int,
    stage_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("manager")),
):
    try:
        return await archive_stage(session, stage_id, user.id, project_id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@stage_router.post(
    "/project/{project_id}/stages/{id}/restore", response_model=BaseShortResponse
)
async def restore_stage_router(
    project_id: int,
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        return await restore_stage(session, id, user.roles, user.id, project_id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")
