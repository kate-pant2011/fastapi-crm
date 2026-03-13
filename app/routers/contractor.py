from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import UserDTO
from app.config.connection import get_db
from app.config.config import ApplicationException
from app.auth.dependencies import require_roles
from app.schemas.common import BaseShortResponse, BaseListResponse
from app.schemas.contractor import (
    ContractorItem,
    ContractorCreation,
    ContractorPatchRequest,
)
from app.services.contractor import (
    get_contractor_list,
    get_contractor,
    create_contractor,
    archive_contractor,
    restore_contractor,
    change_contractor,
)

contractor_router = APIRouter()


@contractor_router.get("/contractor", response_model=BaseListResponse)
async def get_contractor_list_router(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        return await get_contractor_list(session, limit, offset)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@contractor_router.get("/contractor/{id}", response_model=ContractorItem)
async def get_contractor_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        return await get_contractor(session, id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@contractor_router.patch("/contractor/{id}", response_model=ContractorItem)
async def change_branch_router(
    id: int,
    item: ContractorPatchRequest,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        return await change_contractor(session, id, item)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@contractor_router.post("/contractor", response_model=BaseShortResponse)
async def create_contractor_router(
    data: ContractorCreation,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        return await create_contractor(session, data)

    except ApplicationException as e:
        raise HTTPException(
            status_code=e.code, detail={"message": e.name, "payload": e.payload}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@contractor_router.delete("/contractor/{id}", response_model=BaseShortResponse)
async def archive_contractor_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        return await archive_contractor(session, id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@contractor_router.post("/contractor/{id}/restore", response_model=BaseShortResponse)
async def restore_contractor_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        return await restore_contractor(session, id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")
