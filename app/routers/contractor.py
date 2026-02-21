from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.config.connection import get_db
from app.config.config import ApplicationException
from app.auth.dependencies import require_roles
from app.schemas.contractor import ContractorItem, GetContractor, ContractorCreation, CreationResponse, DeletionResponse, RecoveryResponse
from app.services.contractor import form_contractor_list, get_contractor, create_contractor, delete_contractor, restore_contractor


contractor_router = APIRouter()

@contractor_router.get("/contractor", response_model=list[ContractorItem])
async def contractor_list(
    session: AsyncSession = Depends(get_db),
    user_rights: User = Depends(require_roles("owner", "admin", "manager", "executor"))
):
    try:
        return await form_contractor_list(session)
    
    except  ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")

@contractor_router.get("/contractor/{id}", response_model=GetContractor) 
async def contractor_card(
    id: int,
    session: AsyncSession = Depends(get_db),
    user_rights: User = Depends(require_roles("owner", "admin", "manager", "executor"))
):
    try:
       contractor = await get_contractor(session, id)
       return {
           "name": contractor.name,
           "email": contractor.email,
           "description": contractor.description,
           "contractor_companies": contractor.companies,
       }
    
    except  ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")
        

@contractor_router.post("/contractor", response_model=CreationResponse)
async def contractor_creation(
    data: ContractorCreation,
    session: AsyncSession = Depends(get_db),
    user_righths: User = Depends(require_roles("owner", "admin", "manager", "executor"))
):
    try:
        contractor = await create_contractor(session, data)
        return {"contractor_id": contractor.id, "name": contractor.name}
    
    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail={"message": e.name, "payload": e.payload})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")

@contractor_router.delete("/contractor/{id}", response_model=DeletionResponse)
async def contractor_deletion(
    id: int,
    session: AsyncSession = Depends(get_db),
    user_rights: User = Depends(require_roles("owner", "admin", "manager", "executor"))
):
    try:
        result = await delete_contractor(session, id)
        return {"result": result}

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")
    
@contractor_router.patch("/contractor/{id}/restore", response_model=RecoveryResponse)
async def contractor_recovery(
    id: int,
    session: AsyncSession = Depends(get_db),
    user_rights: User = Depends(require_roles("owner", "admin", "manager", "executor"))
):
    try:
        result = await restore_contractor(session, id)
        return {"result": result}
    
    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")        