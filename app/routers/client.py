from fastapi import APIRouter, Depends, HTTPException, Query
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import require_roles
from app.auth.dependencies import UserDTO
from app.config.connection import get_db
from app.schemas.common import BaseShortResponse, BaseListResponse
from app.schemas.client import ClientItem, ClientCreation, ClientPatchRequest
from app.services.client import (
    form_client_list,
    get_client,
    create_client,
    archive_client,
    restore_client,
    change_client,
)
from dataclasses import dataclass

client_router = APIRouter()


@dataclass
class ClientQueryDTO:
    sort: str | None = None
    limit: int = 20
    offset: int = 0
    manager_id: int | None = None
    scope: str | None = None


@client_router.get("/client", response_model=BaseListResponse)
async def client_list(
    scope: str | None = Query(
        default=None, description="mine, scope ignored if manager_id provided"
    ),
    manager_id: int | None = Query(default=None),
    sort: str | None = Query(default=None, description="- stands for desc"),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        query = ClientQueryDTO(
            sort=sort, limit=limit, offset=offset, manager_id=manager_id, scope=scope
        )
        return await form_client_list(
            session=session, roles=user.roles, requester_id=user.id, query=query
        )

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@client_router.get("/client/{id}", response_model=ClientItem)
async def get_client_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        return await get_client(session, user.roles, user.id, id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail={"message": e.name, "payload": e.payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@client_router.patch("/client/{id}", response_model=ClientItem)
async def change_client_router(
    id: int,
    item: ClientPatchRequest,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        return await change_client(session, user.roles, user.id, id, item)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail={"message": e.name, "payload": e.payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@client_router.post("/client", response_model=BaseShortResponse)
async def create_client_router(
    data: ClientCreation,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("manager")),
):
    try:
        return await create_client(session, data, user.id)

    except ApplicationException as e:
        raise HTTPException(
            status_code=e.code, detail={"message": e.name, "payload": e.payload}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@client_router.delete("/client/{id}", response_model=BaseShortResponse)
async def archive_client_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("manager")),
):
    try:
        return await archive_client(session, id, user.id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@client_router.post("/client/{id}/restore", response_model=BaseShortResponse)
async def restore_client_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        return await restore_client(session, id, user.roles, user.id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")
