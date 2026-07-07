from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from typing import Literal
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import require_roles
from app.auth.dependencies import UserDTO
from app.config.connection import get_db
from app.schemas.common import BaseShortResponse, BaseListResponse
from dataclasses import dataclass
from app.schemas.doc_template import (
    DocTemplateItem, 
    DocTemplateCreation, 
    DocTemplatePatchRequest, 
    DocTemplateDeleteResponse, 
    GeneratedDocResponse
)
from app.services.doc_template import (
    get_doc_template_list, 
    get_doc_template, 
    create_doc_template, 
    change_doc_template, 
    delete_doc_template, 
    render_doc_template,
)

@dataclass
class VariablesDTO:
    project_id: int | None 
    client_id: int | None 
    contract_id: int | None 
    company_id: int | None
    stage_id: int | None 
    user_id: int | None 
    branch_id: int | None
    stamp_width_mm: int | None

doc_template_router = APIRouter()


@doc_template_router.get("/doc-template", response_model=BaseListResponse)
async def get_doc_template_list_router(
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
        return await get_doc_template_list(
            session=session, scope=scope, limit=limit, offset=offset, roles=user.roles, user_id=user.id
        )

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@doc_template_router.get("/doc-template/{id}", response_model=DocTemplateItem)
async def get_doc_template_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        return await get_doc_template(session, id, user.roles, user.id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")

    
@doc_template_router.post("/doc-template", response_model=BaseShortResponse)
async def create_doc_template_router(
    name: str = Form(...),
    description: str | None = Form(None),
    is_public: bool = Form(...),
    required_entities: list[str] | None = Form(None),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        data = DocTemplateCreation(
            name=name,
            description=description,
            is_public=is_public,
            required_entities=required_entities
        )
        return await create_doc_template(session, data, user.id, user.roles, file)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@doc_template_router.patch("/doc-template/{id}", response_model=DocTemplateItem)
async def change_doc_template_router(
    data: DocTemplatePatchRequest,
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        return await change_doc_template(session, data, user.id, id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@doc_template_router.delete("/doc-template/{id}", response_model=DocTemplateDeleteResponse)
async def delete_doc_template_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        return await delete_doc_template(session, user.id, id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@doc_template_router.post("/doc-template/{id}/render", response_model=GeneratedDocResponse)
async def render_doc_template_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    project_id: int | None = Query(default=None),
    client_id: int | None = Query(default=None),
    contract_id: int | None = Query(default=None),
    company_id: int | None = Query(default=None),
    stage_id: int | None = Query(default=None),
    user_id: int | None = Query(default=None),
    branch_id: int | None = Query(default=None),
    stamp_width_mm: int | None = Query(default=None),
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
            branch_id=branch_id,
            stamp_width_mm=stamp_width_mm
        )
        return await render_doc_template(session, user.id, user.roles, id, query)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")