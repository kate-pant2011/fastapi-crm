from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.config import ApplicationException
from app.config.connection import get_db
from app.auth.dependencies import require_roles
from app.services.user import create_user, delete_user, restore_user, form_user_list, get_user
from app.schemas.user import UserItem, UserCard, UserCreationRequest, UserCreationResponse, UserDeletionResponse, RecoveryResponse
from app.models.user import User


user_router = APIRouter()


@user_router.get("/user", response_model=list[UserItem])
async def user_list(
    session: AsyncSession = Depends(get_db),
    user_rights: User = Depends(require_roles("owner", "admin", "manager"))
):
    try:
        return await form_user_list(session, user_rights)
    
    except  ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")
    
@user_router.get("/user/{id}", response_model=UserCard)
async def user_card(
    id: int,
    session: AsyncSession = Depends(get_db),
    user_rights: User = Depends(require_roles("owner", "admin", "manager"))
):
    try:
        user = await get_user(session, id, user_rights)
        return {
            "name": user.name,
            "surname": user.surname,
            "position": user.position,
            "email": user.email,
            "branch": user.branch,
            "roles": user.roles
        }
    
    except  ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")
    
@user_router.post("/user", response_model=UserCreationResponse)
async def user_creation(
    data: UserCreationRequest,
    session: AsyncSession = Depends(get_db),
    user_rights: User = Depends(require_roles("owner", "admin"))
):
    try:
        user = await create_user(session, data)
        return {"email": user.email, "password": user.password}
    
    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")

@user_router.delete("/user/{id}", response_model=UserDeletionResponse)
async def user_deletion(
    id: int,
    session: AsyncSession = Depends(get_db),
    user_rights: User = Depends(require_roles("owner", "admin"))
):
    try:
        result = await delete_user(session, id)
    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")

@user_router.patch("/user/{id}/restore", response_model=RecoveryResponse)
async def contractor_recovery(
    id: int,
    session: AsyncSession = Depends(get_db),
    user_rights: User = Depends(require_roles("owner", "admin"))
):
    try:
        result = await restore_user(session, id)
        return {"result": result}
    
    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}") 