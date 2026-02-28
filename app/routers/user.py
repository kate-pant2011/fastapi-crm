from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.config import ApplicationException
from app.config.connection import get_db
from app.auth.dependencies import require_roles
from app.schemas.base import ShortItem
from app.services.user import (
    create_user,
    archive_user,
    restore_user,
    get_user_list,
    get_user,
)
from app.schemas.user import (
    UserItem,
    UserCreationRequest,
    UserCreationResponse
)
from app.auth.dependencies import UserDTO

user_router = APIRouter()


@user_router.get("/user", response_model=list[ShortItem])
async def get_user_list_router(
    session: AsyncSession = Depends(get_db),
    user_rights: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        return await get_user_list(session, user_rights.roles)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@user_router.get("/user/{id}", response_model=UserItem)
async def get_user_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user_rights: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        return await get_user(session, id, user_rights.roles)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@user_router.post("/user", response_model=UserCreationResponse)
async def create_user_router(
    data: UserCreationRequest,
    session: AsyncSession = Depends(get_db),
    user_rights: UserDTO = Depends(require_roles("owner", "admin")),
):
    try:
        return await create_user(session, data)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@user_router.delete("/user/{id}", response_model=ShortItem)
async def archive_user_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user_rights: UserDTO = Depends(require_roles("owner", "admin")),
):
    try:
        return await archive_user(session, id)
    
    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@user_router.post("/user/{id}/restore", response_model=ShortItem)
async def restore_user_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user_rights: UserDTO = Depends(require_roles("owner", "admin")),
):
    try:
        return  await restore_user(session, id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")
