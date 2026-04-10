from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Literal
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import require_roles
from app.auth.dependencies import UserDTO
from app.config.connection import get_db
from app.schemas.common import BaseShortResponse, BaseListResponse
from dataclasses import dataclass
from app.schemas.email_template import (
    EmailTemplateItem, 
    EmailTemplateCreation, 
    EmailTemplatePatchRequest, 
    EmailTemplateDeleteResponse, 
    EmailTemplateShortItem,
    EmailTemplateVars
)
from app.services.email_template import (
    get_email_template_list, 
    get_email_template, 
    create_email_template, 
    change_email_template, 
    delete_email_template, 
    render_email_template,
    get_email_template_vars
)

@dataclass
class VariablesDTO:
    project_id: int | None 
    client_id: int | None 
    contract_id: int | None 
    company_id: int | None
    stage_id: int | None 
    user_id: int | None 

email_template_router = APIRouter()


@email_template_router.get("/email-template/variables", response_model=EmailTemplateVars)
async def get_email_template_vars_router(
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    return get_email_template_vars()


@email_template_router.get("/email-template", response_model=BaseListResponse)
async def get_email_template_list_router(
    session: AsyncSession = Depends(get_db),
    scope: Literal["mine", "available"] | None = Query(
        default=None, 
        description="Filter: mine (only personal), available (shared + personal)"
    ),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        return await get_email_template_list(
            session=session, scope=scope, limit=limit, offset=offset, roles=user.roles, user_id=user.id
        )

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@email_template_router.get("/email-template/{id}", response_model=EmailTemplateItem)
async def get_email_template_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        return await get_email_template(session, id, user.roles, user.id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@email_template_router.post("/email-template", response_model=BaseShortResponse)
async def create_email_template_router(
    data: EmailTemplateCreation,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        return await create_email_template(session, data, user.id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@email_template_router.patch("/email-template/{id}", response_model=EmailTemplateItem)
async def change_email_template_router(
    data: EmailTemplatePatchRequest,
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        return await change_email_template(session, data, user.id, user.roles, id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@email_template_router.delete("/email-template/{id}", response_model=EmailTemplateDeleteResponse)
async def delete_email_template_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        return await delete_email_template(session, user.id, user.roles, id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@email_template_router.get("/email-template/{id}/render", response_model=EmailTemplateShortItem)
async def render_email_template_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    project_id: int | None = Query(default=None),
    client_id: int | None = Query(default=None),
    contract_id: int | None = Query(default=None),
    company_id: int | None = Query(default=None),
    stage_id: int | None = Query(default=None),
    user_id: int | None = Query(default=None),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        query = VariablesDTO(
            project_id=project_id,
            client_id=client_id,
            contract_id=contract_id,
            company_id=company_id,
            stage_id=stage_id,
            user_id=user_id,
        )
        return await render_email_template(session, user.id, user.roles, id, query)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")





