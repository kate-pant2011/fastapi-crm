from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.contract import (
    get_contract_list,
    get_contract,
    create_contract,
    archive_contract,
    restore_contract,
)
from app.schemas.contract import (
    contractCreation, 
    ContractItem, 
    GetcontractItem,
)
from app.auth.dependencies import require_roles, UserDTO
from app.config.connection import get_db
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.common import ShortItem

contract_router = APIRouter()


@contract_router.get("/contract", response_model=list[ContractItem])
async def get_contract_list_router(
    scope: str | None = Query(default=None, description="mine"),
    client_id: int | None = Query(default=None),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        return await get_contract_list(session, user.roles, user.id, scope, client_id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=(f"{type(e).__name__} - {e}"))


@contract_router.get("/contract/{id}", response_model=GetcontractItem)
async def get_contract_router(
    id: int,
    client_id: int | None = Query(default=None),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        return await get_contract(session, user.roles, user.id, id, client_id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@contract_router.post("/contract", response_model=ContractItem)
async def create_contract_router(
    data: contractCreation,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("manager")),
):
    try:
        return await create_contract(session, data, user.id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@contract_router.delete("/contract/{id}", response_model=ShortItem)
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


@contract_router.post("/contract/{id}/restore", response_model=ShortItem)
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
