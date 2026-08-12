from fastapi import APIRouter, Depends, HTTPException, Query, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
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
from .common import organization_patch_form
from app.services.client import get_client

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
            name="error.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="error.html",
            context=context,
            status_code=500,
        )


@company_page_router.get("/companies/create")
async def create_company_page_(
    request: Request,
    client_id: int = Query(),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("manager")
    ),
):
    try:
        client = await get_client(session, user.roles, user.id, client_id)
        context = {
            "request": request,
            "user": user,
            "create_url": "/companies/create",
            "client_id": client_id,
            "client_name": client.name,
        }

        return templates.TemplateResponse(
            request=request,
            name="company/create.html",
            context=context,
        )
    except ApplicationException as e:
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, 
            name="error.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="error.html",
            context=context,
            status_code=500,
        )

@company_page_router.post("/companies/create")
async def create_company_page(
    request: Request,
    name: str = Form(...),
    inn: str = Form(...),
    client_id: int = Form(...),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_page_roles("manager")),
):
    context = {
        "request": request,
        "user": user,
        "create_url": "companies/create",
        "return_url": "/companies",
        "error": None,
    }

    data = CompanyCreation(name=name, inn=inn, client_id=client_id)

    try:
        result = await create_company(session, data, user.id)

        context.update(
            {
                "id": result.id,
                "name": result.name,
                "form_data": {
                    "name": name,
                    "inn": inn,
                    "client_id": client_id
                }
            }
        )

        return templates.TemplateResponse(
            request=request,
            name="archived_restored.html",
            context=context,
        )

    except ApplicationException as e:
        await session.rollback()
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, 
            name="error.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        await session.rollback()
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="error.html",
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
        "restore_url": f"/companies/{company_id}/restore",
        "email_url":f"/email-templates?company_id={company_id}", 
        "document_url":f"/doc-templates?company_id={company_id}", 
        "return_url": "/companies",
        "error": None,
    }

    try:
        result = await get_company(session, user.roles, user.id, company_id)

        context.update(
            {
                "name": result.name,
                "is_archived": result.is_archived,
                "inn": result.inn,
                "client": result.client,
                "contracts": result.contracts,
                "kpp": result.kpp,
                "ogrn": result.ogrn,
                "okpo": result.okpo,
                "okved": result.okved,
                "okfs": result.okfs,
                "okopf": result.okopf,
                "okato": result.okato,
                "legal_address": result.legal_address,
                "address": result.address,
                "email": result.email,
                "telephone": result.telephone,
                "website": result.website,
                "director_full_name": result.director_full_name,
                "director_short_name": result.director_short_name,
                "director_position": result.director_position,
                "authority_document": result.authority_document,
                "bank_name": result.bank_name,
                "bik": result.bik,
                "checking_account": result.checking_account, 
                "correspondent_account": result.correspondent_account,
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
            request=request, name="error.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="error.html",
            context=context,
            status_code=500,
        )


@company_page_router.post("/companies/{company_id}/delete")
async def company_delete_page(
    request: Request,
    company_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("manager")
    ),
):

    context = {
        "request": request,
        "user": user,
        "branch_id": company_id, 
        "detail_url": f"/companies/{company_id}",
        "return_url": f"/companies/{company_id}",
        "error": None,
    }

    try:
        result = await archive_company(session, company_id, user.id)

        context.update(
            {
                "name": result.name,
                "message": "удаление",
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="archived_restored.html",
            context=context,
        )

    except ApplicationException as e:
        await session.rollback()
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, name="error.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        await session.rollback()
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="error.html",
            context=context,
            status_code=500,
        )


@company_page_router.post("/companies/{company_id}/restore")
async def company_restore_page(
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
        "branch_id": company_id, 
        "detail_url": f"/companies/{company_id}",
        "return_url": f"/companies/{company_id}",
        "error": None,
    }

    try:
        result = await restore_company(session, company_id, user.roles, user.id)

        context.update(
            {
                "name": result.name,
                "message": "восстановление",
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="archived_restored.html",
            context=context,
        )

    except ApplicationException as e:
        await session.rollback()
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, name="error.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        await session.rollback()
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="error.html",
            context=context,
            status_code=500,
        )


@company_page_router.get("/companies/{id}/edit")
async def edit_company_page(
    request: Request,
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles(
            "owner", "admin", "manager", 
        )
    ),
):
    context = {
        "request": request,
        "user": user,
        "edit_url": f"/companies/{id}/edit",
        "error": None,
        "return_url": "/companies",
    }
    
    try:
        result = await get_company(session, user.roles, user.id, id)

        context["template"] = result

        return templates.TemplateResponse(
            request=request,
            name="company/edit.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__}: {e}"

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context=context,
            status_code=500,
        )


@company_page_router.post("/companies/{id}/edit")
async def company_template(
    request: Request,
    id: int,
    item: CompanyPatchRequest = Depends(organization_patch_form),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles(
            "owner", "admin", "manager"
        )
    ),
):
    context = {
        "request": request,
        "user": user,
        "edit_url": f"/companies/{id}/edit",
        "return_url": "/companies",
        "error": None,
    }
    
    try:
        data = item.model_dump(exclude_none=True)

        company_item = CompanyPatchRequest(**data)

        result = await change_company(session, user.roles, user.id, id, company_item)

        context["template"] = result

        return RedirectResponse(
            url=f"/companies/{id}",
            status_code=303,
        )

    except ApplicationException as e:
        await session.rollback()
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        await session.rollback()
        context["error"] = f"{type(e).__name__}: {e}"

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context=context,
            status_code=500,
        )