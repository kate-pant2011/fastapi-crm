from fastapi import APIRouter, HTTPException, Depends
from app.config.config import ApplicationException
from app.auth.dependencies import require_roles
from app.schemas.branch import BranchesItem, BranchItem, BranchCreationRequest,BranchCreationResponse, BranchDeletionResponse, BranchRecoveryResponse
from app.services.branch import create_branch, delete_existing_branch, restore_branch, form_branch_list, get_branch
from app.models.user import User
from app.config.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession

branch_router = APIRouter()

@branch_router.get("/branch", response_model=list[BranchesItem])
async def branch_list(
    session: AsyncSession = Depends(get_db),
    user_rights: User = Depends(require_roles("owner", "admin", "manager", "executor"))
):
    try:
        return await form_branch_list(session)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")
    
    except  ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)
    
@branch_router.get("/branch/{id}", response_model=BranchItem)
async def branch_card(
    id: int,
    session: AsyncSession = Depends(get_db),
    user_rights: User = Depends(require_roles("owner", "admin", "manager", "executor"))  
):
    try:
        return await get_branch(session, id)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")
    
    except  ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)


@branch_router.post("/branch", response_model=BranchCreationResponse)
async def branch_creation(
    input: BranchCreationRequest, 
    session: AsyncSession = Depends(get_db),
    user_rights: User = Depends(require_roles("owner", "admin"))
):
    try:
        return await create_branch(session, input.inn, input.branch_name)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")
    
    except  ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

@branch_router.delete("/branch/{inn}", response_model=BranchDeletionResponse)
async def branch_deletion(
    inn: str, 
    session: AsyncSession = Depends(get_db),
    user_rights: User = Depends(require_roles("owner", "admin"))
):
    try:
        result = await delete_existing_branch(session, inn)
        return {"result": result}
    
    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")

@branch_router.patch("/branch/{inn}/restore", response_model=BranchRecoveryResponse)
async def branch_recovery(
    inn: str,
    session: AsyncSession = Depends(get_db),
    user_rights: User = Depends(require_roles("owner", "admin"))
):
    try:
        result = await restore_branch(session, inn)
        return {"result": result}
    
    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")      