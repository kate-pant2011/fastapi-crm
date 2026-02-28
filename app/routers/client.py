from fastapi import APIRouter, Depends, HTTPException, Query
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import require_roles
from app.auth.dependencies import UserDTO
from app.config.connection import get_db
from app.schemas.base import ShortItem
from app.schemas.client import (
    ClientItem,
    ClientCreation,
)
from app.services.client import (
    form_client_list,
    get_client,
    create_client,
    archive_client,
    restore_client,
)

client_router = APIRouter()


@client_router.get("/client", response_model=list[ShortItem])
async def client_list(
    scope: str | None = Query(default=None, description="mine"),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_roles("owner", "admin", "manager")
    ),
):
    try:
        return await form_client_list(session, user.roles, user.id, scope)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@client_router.get("/client/{id}", response_model=ClientItem)
async def get_client_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_roles("owner", "admin", "manager")
    ),
):
    try:
        return await get_client(session, user.roles, user.id, id) 

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@client_router.post("/client", response_model=ShortItem)
async def create_client_router(
    data: ClientCreation,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_roles("manager")
    ),
):
    try:
        return await create_client(session, data, user.id)

    except ApplicationException as e:
        raise HTTPException(
            status_code=e.code, detail={"message": e.name, "payload": e.payload}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@client_router.delete("/client/{id}", response_model=ShortItem)
async def archive_client_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_roles("manager")
    ),
):
    try:
        return await archive_client(session, id, user.id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@client_router.post("/client/{id}/restore", response_model=ShortItem)
async def restore_client_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_roles("owner", "admin", "manager")
    ),
):
    try:
        return await restore_client(session, id, user.roles,  user.id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")