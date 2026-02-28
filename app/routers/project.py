from fastapi import APIRouter, Depends, HTTPException, Query
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import require_roles
from app.auth.dependencies import UserDTO
from app.config.connection import get_db
from app.schemas.base import ShortItem
from app.schemas.project import (
    ProjectItem,
    ProjectCreation,
)
from app.services.project import (
    get_project_list,
    get_project,
    create_project,
    archive_project,
    restore_project
)

project_router = APIRouter()


@project_router.get("/project", response_model=list[ShortItem])
async def get_project_list_router(
    scope: str | None = Query(default=None, description="mine"),
    client_id: int | None = Query(default=None),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_roles("owner", "admin", "manager")
    ),
):
    try:
        return await get_project_list(session, user.roles, user.id, scope, client_id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@project_router.get("/project/{id}", response_model=ProjectItem)
async def get_project_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_roles("owner", "admin", "manager")
    ),
):
    try:
        return await get_project(session, user.roles, user.id, id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@project_router.post("/project", response_model=ShortItem)
async def create_project_router(
    data: ProjectCreation,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_roles("manager")
    ),
):
    try:
        return await create_project(session, data, user.id)

    except ApplicationException as e:
        raise HTTPException(
            status_code=e.code, detail={"message": e.name, "payload": e.payload}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")

@project_router.delete("/project/{id}", response_model=ShortItem)
async def archive_project_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_roles("manager")
    ),
):
    try:
        return await archive_project(session, id, user.id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@project_router.post("/project/{id}/restore", response_model=ShortItem)
async def restore_project_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_roles("owner", "admin", "manager")
    ),
):
    try:
        return await restore_project(session, id, user.roles,  user.id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")