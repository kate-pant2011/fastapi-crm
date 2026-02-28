from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.company import (
    get_company_list, 
    get_company, 
    create_company,
    archive_company,
    restore_company
)
from app.schemas.company import CompanyCreation, CompanyItem
from app.schemas.base import ShortItem
from app.auth.dependencies import require_roles, UserDTO
from app.config.connection import get_db
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession

company_router = APIRouter()

@company_router.get("/company", response_model=list[ShortItem])
async def get_company_list_router(
    scope: str | None =  Query(default=None, description="mine"),
    client_id: int | None = Query(default=None),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager"))
):
    try:
        return await get_company_list(session, user.roles, user.id, scope, client_id)
    
    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=(f"{type(e).__name__} - {e}"))

@company_router.get("/company/{id}", response_model=CompanyItem)
async def get_company_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_roles("owner", "admin", "manager")
    ),
):
    try:
        return await get_company(session, user.roles, user.id, id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@company_router.post("/company", response_model=ShortItem)
async def create_company_router(
    data: CompanyCreation,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_roles("manager")
    ),
):
    try:
        return await create_company(session, data, user.id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")

@company_router.delete("/company/{id}", response_model=ShortItem)
async def archive_company_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_roles("manager")
    ),
):
    try:
        return await archive_company(session, id, user.id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@company_router.post("/company/{id}/restore", response_model=ShortItem)
async def restore_company_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_roles("owner", "admin", "manager")
    ),
):
    try:
        return await restore_company(session, id, user.roles,  user.id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")