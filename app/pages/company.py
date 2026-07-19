from fastapi import APIRouter, Depends, HTTPException, Query, Form, Request
from fastapi.templating import Jinja2Templates
from app.services.client import form_client_list
from app.services.company import (
    get_company_list,
    get_company,
    create_company,
    archive_company,
    restore_company,
    change_company,
)
from app.schemas.company import CompanyCreation, CompanyItem, CompanyPatchRequest
from app.schemas.common import BaseShortResponse, BaseListResponse
from app.auth.dependencies import require_page_roles, UserDTO
from app.config.connection import get_db
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Literal
from app.routers.company import CompanyQueryDTO
from app.routers.client import ClientQueryDTO

company_page_router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)


@company_page_router.get("/companies")
async def company_list_page(
    request: Request,
    scope: Literal["mine"] | None = Query(
        default=None, description="scope ignored if manager_id provided"
    ),
    client_id: int | None = Query(default=None),
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
        "companies": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
        "sort": sort,
        "client_id": client_id,
        "scope": scope,
        "error": None,
    }
    try:
        query = CompanyQueryDTO(
            sort=sort,
            limit=limit,
            offset=offset,
            client_id=client_id,
            scope=scope
        )
        result = await get_company_list(
            session=session, roles=user.roles, requester_id=user.id, query=query
        )

        clients_result = await form_client_list(
            session=session, roles=user.roles, requester_id=user.id, query=ClientQueryDTO(limit=1000)
        )

        context.update(
            {
                "companies": result.get("items", []),
                "total": result.get("total", 0),
                "limit": result.get("limit", limit),
                "offset": result.get("offset", offset),
                "clients": clients_result.get("items", [])
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="company/list.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, 
            name="company/list.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="company/list.html",
            context=context,
            status_code=500,
        )


@company_page_router.get("/companies/{company_id}")
async def company_detail_page(
    request: Request,
    company_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager")
    ),
):

    context = {
        "request": request,
        "user": user,
        "company_id": company_id,
        "edit_url": f"/companies/{company_id}/edit",
        "delete_url": f"/companies/{company_id}/delete",
        "email_url":f"/email-form?company_id={company_id}", 
        "document_url":f"/document-form?company_id={company_id}", 
        "error": None,
    }

    try:
        result = await get_company(session, user.roles, user.id, company_id)

        context.update(
            {
                "name": result.name,
                "inn": result.inn,
                "client": result.client,
                "contracts": result.contracts,
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="company/detail.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, name="company/detail.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="company/detail.html",
            context=context,
            status_code=500,
        )


