from fastapi import APIRouter, Depends, HTTPException, Query, Form, Request
from fastapi.templating import Jinja2Templates
from app.auth.dependencies import require_page_roles, UserDTO
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.connection import get_db
from dataclasses import dataclass
from app.schemas.common import BaseShortResponse, BaseListResponse
from app.schemas.project import ProjectItem, ProjectCreation, ProjectPatchRequest
from app.services.project import (
    get_project_list,
    get_project,
    create_project,
    archive_project,
    restore_project,
    change_project,
)
from typing import Literal
from app.routers.project import ProjectQueryDTO
from app.routers.contract import ContractQueryDTO
from app.routers.client import ClientQueryDTO
from app.services.client import form_client_list
from app.services.contract import get_contract_list

project_page_router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)


@project_page_router.get("/projects")
async def project_list_page(
    request: Request,
    scope: Literal["mine"] | None = Query(
        default=None, description="scope ignored if manager_id provided"
    ),
    client_id: int | None = Query(default=None),
    contract_id: int | None = Query(default=None),
    is_archived: bool | None = Query(default=None),
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
        "projects": [],
        "clients": [],
        "contracts": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
        "sort": sort,
        "client_id": client_id,
        "contract_id": contract_id,
        "is_archived": is_archived,
        "scope": scope,
        "error": None,
    }
    try:
        query = ProjectQueryDTO(
            sort=sort,
            limit=limit,
            offset=offset,
            contract_id=contract_id,
            client_id=client_id,
            is_archived=is_archived,
            scope=scope
        )
        result = await get_project_list(
            session=session, roles=user.roles, requester_id=user.id, query=query
        )

        clients_result = await form_client_list(
            session=session, roles=user.roles, requester_id=user.id, query=ClientQueryDTO(limit=1000)
        )
        contracts_result = await get_contract_list(
            session=session, roles=user.roles, requester_id=user.id, query=ContractQueryDTO(limit=1000)
        )
        context.update(
            {
                "projects": result.get("items", []),
                "total": result.get("total", 0),
                "limit": result.get("limit", limit),
                "offset": result.get("offset", offset),
                "clients": clients_result.get("items", []),
                "contracts": contracts_result.get("items", []),
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="project/list.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, 
            name="project/list.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="project/list.html",
            context=context,
            status_code=500,
        )


@project_page_router.get("/projects/{project_id}")
async def project_detail_page(
    request: Request,
    project_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor")
    ),
):

    context = {
        "request": request,
        "user": user,
        "project_id": project_id,
        "edit_url": f"/projects/{project_id}/edit",
        "delete_url": f"/projects/{project_id}/delete",
        "email_url":f"/email-form?project_id={project_id}", 
        "document_url":f"/document-form?project_id={project_id}", 
        "error": None,
    }

    try:
        result = await get_project(session, user.roles, user.id, project_id)

        context.update(
            {
                "name": result.get("name"),
                "description":  result.get("description"),
                "start_date":  result.get("start_date"),
                "end_date":  result.get("end_date"),
                "client_name":  result.get("client_name"),
                "client_email":  result.get("client_email"),
                "contract":  result.get("contract"),
                "manager":  result.get("manager"),
                "stages":  result.get("stages"),
                "files": result.get("files")
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="project/detail.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, name="project/detail.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="project/detail.html",
            context=context,
            status_code=500,
        )