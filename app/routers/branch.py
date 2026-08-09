from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse
from app.config.config import ApplicationException
from app.auth.dependencies import require_roles, UserDTO
from app.schemas.common import BaseShortResponse, LegalEntityListResponse
from app.schemas.branch import BranchItem, BranchCreationRequest, BranchPatchRequest
from app.services.branch import (
    create_branch,
    archive_branch,
    restore_branch,
    get_branch_list,
    get_branch,
    change_branch,
    delete_stamp,
    download_stamp
)
from app.config.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from dataclasses import dataclass

branch_router = APIRouter()


@dataclass
class BranchQueryDTO:
    sort: str | None = None
    limit: int = 20
    offset: int = 0
    is_archived: bool | None = None


@branch_router.get("/branch", response_model=LegalEntityListResponse)
async def get_branch_list_router(
    sort: str | None = Query(default=None, description="- stands for desc"),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    is_archived: bool | None = Query(default=None),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        query = BranchQueryDTO(sort=sort, limit=limit, offset=offset, is_archived=is_archived)
        return await get_branch_list(session, query)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@branch_router.get("/branch/{id}", response_model=BranchItem)
async def get_branch_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        return await get_branch(session, id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail={"message": e.name, "payload": e.payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@branch_router.patch("/branch/{id}", response_model=BranchItem)
async def change_branch_router(
    id: int,
    item: BranchPatchRequest,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin")),
):
    try:
        return await change_branch(session, id, item)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail={"message": e.name, "payload": e.payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@branch_router.post("/branch", response_model=BaseShortResponse)
async def create_branch_router(
    branch: BranchCreationRequest,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin")),
):
    try:
        return await create_branch(session, branch.inn, branch.name)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail={"message": e.name, "payload": e.payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@branch_router.delete("/branch/{id}", response_model=BaseShortResponse)
async def archive_branch_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin")),
):
    try:
        return await archive_branch(session, id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@branch_router.post("/branch/{id}/restore", response_model=BaseShortResponse)
async def restore_branch_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin")),
):
    try:
        return await restore_branch(session, id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@branch_router.get("/branch/{branch_id}/stamp")
async def download_branch_stamp(
    branch_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin")),
):
    try:
        file = await download_stamp(session, branch_id, user.id)
        return FileResponse(path=file.path, filename=file.name, media_type=file.mime_type) 

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")
    

@branch_router.delete("/branch/{branch_id}/stamp", response_model=BaseShortResponse)
async def delete_branch_stamp(
    branch_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin")),
):
    try:
        return await delete_stamp(session, branch_id, user.id, user.roles)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")