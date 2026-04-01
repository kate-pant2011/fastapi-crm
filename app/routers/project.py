from fastapi import APIRouter, Depends, HTTPException, Query
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import require_roles
from app.auth.dependencies import UserDTO
from app.config.connection import get_db
from dataclasses import dataclass
from app.schemas.common import BaseShortResponse, BaseListResponse
from app.schemas.project import ProjectItem, ProjectCreation, ProjectPatchRequest
from app.services.project import (
    get_project_list,
    get_project,
    create_project,
    archive_project,
    restore_project,
    change_project,
)

project_router = APIRouter()


@dataclass
class QueryDTO:
    scope: str | None
    client_id: int | None
    contract_id: int | None
    is_archived: bool | None
    sort: str | None
    limit: int
    offset: int


@project_router.get("/project", response_model=BaseListResponse)
async def get_project_list_router(
    sort: str | None = Query(default=None, description="- stands for desc"),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    scope: str | None = Query(default=None, description="mine"),
    client_id: int | None = Query(default=None),
    contract_id: int | None = Query(default=None),
    is_archived: bool | None = Query(default=None),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        project = QueryDTO(
            scope=scope,
            client_id=client_id,
            contract_id=contract_id,
            is_archived=is_archived,
            sort=sort,
            limit=limit,
            offset=offset,
        )
        return await get_project_list(
            session=session, roles=user.roles, requester_id=user.id, query=project
        )

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@project_router.get("/project/{id}", response_model=ProjectItem)
async def get_project_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        return await get_project(session, user.roles, user.id, id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail={"message": e.name, "payload": e.payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@project_router.patch("/project/{id}", response_model=ProjectItem)
async def change_project_router(
    id: int,
    item: ProjectPatchRequest,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        return await change_project(session, user.roles, user.id, id, item)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail={"message": e.name, "payload": e.payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@project_router.post("/project", response_model=BaseShortResponse)
async def create_project_router(
    data: ProjectCreation,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("manager")),
):
    try:
        return await create_project(session, data, user.id)

    except ApplicationException as e:
        raise HTTPException(
            status_code=e.code, detail={"message": e.name, "payload": e.payload}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@project_router.delete("/project/{id}", response_model=BaseShortResponse)
async def archive_project_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("manager")),
):
    try:
        return await archive_project(session, id, user.id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@project_router.post("/project/{id}/restore", response_model=BaseShortResponse)
async def restore_project_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        return await restore_project(session, id, user.roles, user.id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")
