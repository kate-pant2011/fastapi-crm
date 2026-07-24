from fastapi import APIRouter, Depends, HTTPException, Query, Form, Request
from fastapi.templating import Jinja2Templates
from app.services.company import get_company_list
from app.services.branch import get_branch_list
from app.services.contract import (
    get_contract_list,
    get_contract,
    create_contract,
    archive_contract,
    restore_contract,
    change_contract,
)
from app.schemas.contract import (
    СontractCreation,
    ContractItem,
    ContractListResponse,
    GetContractItem,
    ContractPatchRequest,
)
from app.auth.dependencies import require_page_roles, UserDTO
from app.config.connection import get_db
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.common import BaseShortResponse
from typing import Literal
from app.routers.company import CompanyQueryDTO
from app.routers.contract import ContractQueryDTO
from app.routers.branch import BranchQueryDTO


contract_page_router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)


@contract_page_router.get("/contracts")
async def contract_list_page(
    request: Request,
    scope: Literal["mine"] | None = Query(
        default=None, description="scope ignored if manager_id provided"
    ),
    branch_id: int | None = Query(default=None),
    company_id: int | None = Query(default=None),
    sort: str | None = Query(default=None),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager"))
):
    context = {
        "request": request,
        "user": user,
        "contracts": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
        "sort": sort,
        "company_id": company_id,
        "branch_id": branch_id,
        "scope": scope,
        "error": None,
    }
    try:
        query = ContractQueryDTO(
            sort=sort,
            limit=limit,
            offset=offset,
            company_id=company_id,
            branch_id=branch_id,
            scope=scope
        )
        result = await get_contract_list(
            session=session, roles=user.roles, requester_id=user.id, query=query
        )
        companies_result = await get_company_list(
            session=session, roles=user.roles, requester_id=user.id, query=CompanyQueryDTO(limit=1000)
        )
        branches_result = await get_branch_list(
            session=session, query=BranchQueryDTO(limit=1000)
        )

        context.update(
            {
                "contracts": result.get("items", []),
                "total": result.get("total", 0),
                "limit": result.get("limit", limit),
                "offset": result.get("offset", offset),
                "companies": companies_result.get("items", []),
                "branches": branches_result.get("items", [])
            }
        )

        return templates.TemplateResponse(
            request=request,
            name="contract/list.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, 
            name="contract/list.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="contract/list.html",
            context=context,
            status_code=500,
        )


@contract_page_router.get("/contracts/{contract_id}")
async def contract_detail_page(
    request: Request,
    contract_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager")
    ),
):

    context = {
        "request": request,
        "user": user,
        "contract_id": contract_id,
        "edit_url": f"/contracts/{contract_id}/edit",
        "delete_url": f"/contracts/{contract_id}/delete",
        "restore_url": f"/contracts/{contract_id}/restore",
        "email_url":f"/email-form?contract_id={contract_id}", 
        "document_url":f"/doc-templates?contract_id={contract_id}", 
        "error": None,
    }

    try:
        result = await get_contract(session, user.roles, user.id, contract_id)

        context.update(
            {
                "number": result.number,
                "status": result.status,
                "name": result.name,
                "description": result.description,
                "valid_from": result.valid_from,
                "valid_to": result.valid_to,
                "branch": result.branch,
                "company": result.company,
                "is_archived": result.is_archived,
            }
        )

        return templates.TemplateResponse(
            request=request,
            name="contract/detail.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, name="contract/detail.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="contract/detail.html",
            context=context,
            status_code=500,
        )


@contract_page_router.post("/contracts/{contract_id}/delete")
async def contract_delete_page(
    request: Request,
    contract_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("manager")
    ),
):

    context = {
        "request": request,
        "user": user,
        "contract_id": contract_id, 
        "detail_url": f"/contracts/{contract_id}",
        "error": None,
    }

    try:
        result = await archive_contract(session, contract_id, user.id)

        context.update(
            {
                "name": result.name,
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="archived_restored.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, name="archived_restored.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="archived_restored.html",
            context=context,
            status_code=500,
        )


@contract_page_router.post("/contracts/{contract_id}/restore")
async def contract_restore_page(
    request: Request,
    contract_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager")
    ),
):

    context = {
        "request": request,
        "user": user,
        "contract_id": contract_id, 
        "detail_url": f"/contracts/{contract_id}",
        "error": None,
    }

    try:
        result = await restore_contract(session, contract_id, user.roles, user.id)

        context.update(
            {
                "name": result.name,
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="archived_restored.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, name="archived_restored.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="archived_restored.html",
            context=context,
            status_code=500,
        )