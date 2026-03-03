from fastapi import APIRouter, HTTPException, Depends
from app.config.config import ApplicationException
from app.auth.dependencies import require_roles
from app.schemas.common import ShortItem
from app.schemas.branch import (
    BranchItem,
    BranchCreationRequest,
)
from app.services.branch import (
    create_branch,
    archive_branch,
    restore_branch,
    form_branch_list,
    get_branch,
)
from app.auth.dependencies import UserDTO
from app.config.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession

branch_router = APIRouter()


@branch_router.get("/branch", response_model=list[ShortItem])
async def branch_list(
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        return await form_branch_list(session)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)


@branch_router.get("/branch/{id}", response_model=BranchItem)
async def get_branch_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        return await get_branch(session, id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)


@branch_router.post("/branch", response_model=ShortItem)
async def create_branch_router(
    branch: BranchCreationRequest,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin")),
):
    try:
        return await create_branch(session, branch.inn, branch.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)


@branch_router.delete("/branch/{id}", response_model=ShortItem)
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


@branch_router.post("/branch/{id}/restore", response_model=ShortItem)
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
