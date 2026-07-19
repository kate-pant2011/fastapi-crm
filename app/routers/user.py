from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.config import ApplicationException
from app.config.connection import get_db
from app.auth.dependencies import require_roles
from app.schemas.common import BaseShortResponse, BaseListResponse
from app.services.user import (
    create_user,
    archive_user,
    restore_user,
    get_user_list,
    get_user,
    get_user_me,
    change_user,
    resend_signup_invitation
)
from app.schemas.user import (
    UserItem,
    UserCreationRequest,
    UserCreationResponse,
    UserPatchRequest,
)
from app.auth.dependencies import UserDTO
from dataclasses import dataclass

user_router = APIRouter()


@dataclass
class QueryDTO:
    branch_id: int | None = None
    is_active: bool | None = None
    role_name: str | None = None
    sort: str | None = None
    limit: int = 100
    offset: int = 0


@user_router.get("/user", response_model=BaseListResponse)
async def get_user_list_router(
    branch_id: int | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    role_name: str | None = Query(default=None),
    sort: str | None = Query(default=None, description="- stands for desc"),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        query = QueryDTO(
            branch_id=branch_id,
            is_active=is_active,
            role_name=role_name,
            sort=sort,
            limit=limit,
            offset=offset,
        )
        return await get_user_list(session=session, roles=user.roles, query=query)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@user_router.get("/user/me", response_model=UserItem)
async def get_user_router(
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        return await get_user_me(session, user.id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail={"message": e.name, "payload": e.payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@user_router.get("/user/{id}", response_model=UserItem)
async def get_user_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        return await get_user(session, id, user.roles)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail={"message": e.name, "payload": e.payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@user_router.patch("/user/{id}", response_model=BaseShortResponse)
async def change_user_router(
    id: int,
    item: UserPatchRequest,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin")),
):
    try:
        return await change_user(session, user.roles, id, item)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail={"message": e.name, "payload": e.payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@user_router.post("/user", response_model=UserCreationResponse)
async def create_user_router(
    data: UserCreationRequest,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin")),
):
    try:
        return await create_user(session, user.roles, data)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail={"message": e.name, "payload": e.payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@user_router.delete("/user/{id}", response_model=BaseShortResponse)
async def archive_user_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin")),
):
    try:
        return await archive_user(session, id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@user_router.post("/user/{id}/restore", response_model=BaseShortResponse)
async def restore_user_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin")),
):
    try:
        return await restore_user(session, id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@user_router.post("/user/{id}/resend-invitation", response_model=UserCreationResponse)
async def resend_invitation(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin")),
):
    try:
        return await resend_signup_invitation(session, id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")