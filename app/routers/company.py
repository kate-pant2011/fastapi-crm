from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.company import (
    get_company_list,
    get_company,
    create_company,
    archive_company,
    restore_company,
    change_company,
)
from app.schemas.company import CompanyCreation, CompanyItem, CompanyPatchRequest
from app.schemas.common import BaseShortResponse, BaseListResponse
from app.auth.dependencies import require_roles, UserDTO
from app.config.connection import get_db
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession
from dataclasses import dataclass

company_router = APIRouter()


@dataclass
class QueryDTO:
    sort: str | None
    limit: int
    offset: int
    client_id: int | None
    scope: str | None


@company_router.get("/companies", response_model=BaseListResponse)
async def get_company_list_router(
    scope: str | None = Query(default=None, description="mine, scope ignored if manager_id provided"),
    client_id: int | None = Query(default=None),
    sort: str | None = Query(default=None, description="- stands for desc"),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        query = QueryDTO(
            sort=sort, limit=limit, offset=offset, client_id=client_id, scope=scope
        )
        return await get_company_list(
            session=session, roles=user.roles, requester_id=user.id, query=query
        )

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=(f"{type(e).__name__} - {e}"))


@company_router.get("/companies/{id}", response_model=CompanyItem)
async def get_company_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        return await get_company(session, user.roles, user.id, id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail={"message": e.name, "payload": e.payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@company_router.patch("/companies/{id}", response_model=CompanyItem)
async def change_company_router(
    id: int,
    item: CompanyPatchRequest,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        return await change_company(session, user.roles, user.id, id, item)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail={"message": e.name, "payload": e.payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@company_router.post("/companies", response_model=BaseShortResponse)
async def create_company_router(
    data: CompanyCreation,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("manager")),
):
    try:
        return await create_company(session, data, user.id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail={"message": e.name, "payload": e.payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@company_router.delete("/companies/{id}", response_model=BaseShortResponse)
async def archive_company_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("manager")),
):
    try:
        return await archive_company(session, id, user.id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@company_router.post("/companies/{id}/restore", response_model=BaseShortResponse)
async def restore_company_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        return await restore_company(session, id, user.roles, user.id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")
