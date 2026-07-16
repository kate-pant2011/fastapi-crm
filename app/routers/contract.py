from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.contract import (
    get_contract_list,
    get_contract,
    create_contract,
    archive_contract,
    restore_contract,
    change_contract,
)
from app.schemas.contract import (
    СontractCreation,
    ContractItem,
    ContractListResponse,
    GetContractItem,
    ContractPatchRequest,
)
from app.auth.dependencies import require_roles, UserDTO
from app.config.connection import get_db
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.common import BaseShortResponse
from dataclasses import dataclass

contract_router = APIRouter()


@dataclass
class QueryDTO:
    sort: str | None
    limit: int
    offset: int
    scope: str | None
    branch_id: int | None
    company_id: int | None


@contract_router.get("/contracts", response_model=ContractListResponse)
async def get_contract_list_router(
    scope: str | None = Query(default=None, description="mine"),
    branch_id: int | None = Query(default=None),
    company_id: int | None = Query(default=None),
    sort: str | None = Query(default=None, description="- stands for desc"),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    query = QueryDTO(
        sort=sort,
        limit=limit,
        offset=offset,
        branch_id=branch_id,
        company_id=company_id,
        scope=scope,
    )
    try:
        return await get_contract_list(
            session=session, roles=user.roles, requester_id=user.id, query=query
        )

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=(f"{type(e).__name__} - {e}"))


@contract_router.get("/contracts/{id}", response_model=GetContractItem)
async def get_contract_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        return await get_contract(session, user.roles, user.id, id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail={"message": e.name, "payload": e.payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@contract_router.patch("/contracts/{id}", response_model=GetContractItem)
async def change_contract_router(
    id: int,
    item: ContractPatchRequest,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        return await change_contract(session, user.roles, user.id, id, item)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail={"message": e.name, "payload": e.payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@contract_router.post("/contracts", response_model=ContractItem)
async def create_contract_router(
    data: СontractCreation,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("manager")),
):
    try:
        return await create_contract(session, data, user.id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@contract_router.delete("/contracts/{id}", response_model=ContractItem)
async def archive_contract_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("manager")),
):
    try:
        return await archive_contract(session, id, user.id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@contract_router.post("/contracts/{id}/restore", response_model=ContractItem)
async def restore_contract_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        return await restore_contract(session, id, user.roles, user.id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")
