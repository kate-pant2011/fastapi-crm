from fastapi import APIRouter, Depends, HTTPException, UploadFile, Query, File, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
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
from app.services.stage import get_stage_list
from app.services.stage_template import get_stage_template_list
from typing import Literal
from app.routers.project import ProjectQueryDTO
from app.routers.contract import ContractQueryDTO
from app.routers.client import ClientQueryDTO
from app.routers.stage import StageQueryDTO
from app.services.client import form_client_list
from app.services.contract import get_contract_list
from app.services.file import get_file_for_download, get_file_list, get_file, upload_file, delete_file
from app.routers.file import FileQueryDTO
from app.services.client import get_client
from datetime import datetime
from app.services.company import get_company_list
from app.routers.company import CompanyQueryDTO

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


@project_page_router.get("/projects/create")
async def create_project_page_(
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
            "create_url": "/projects/create",
            "client_id": client_id,
            "client_name": client.name,
        }

        return templates.TemplateResponse(
            request=request,
            name="project/create.html",
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

@project_page_router.post("/projects/create")
async def create_project_page(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    start_date: datetime = Form(...),
    end_date: datetime = Form(...),
    client_id: int = Form(...),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_page_roles("manager")),
):
    context = {
        "request": request,
        "user": user,
        "create_url": "projects/create",
        "return_url": "/projects",
        "error": None,
    }

    data = ProjectCreation(
        name=name, 
        description=description, 
        client_id=client_id,
        start_date=start_date,
        end_date=end_date
    )

    try:
        result = await create_project(session, data, user.id)

        context.update(
            {
                "id": result.id,
                "name": result.name,
                "form_data": {
                    "name": name,
                    "description": description,
                    "start_date": start_date,
                    "end_date": end_date,
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


@project_page_router.get("/projects/{project_id}")
async def project_detail_page(
    request: Request,
    project_id: int,
    session: AsyncSession = Depends(get_db),
    sort: str | None = Query(default=None),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor")
    ),
):

    context = {
        "request": request,
        "user": user,
        "total": 0,
        "limit": limit,
        "offset": offset,
        "sort": sort,
        "project_id": project_id,
        "edit_url": f"/projects/{project_id}/edit",
        "delete_url": f"/projects/{project_id}/delete",
        "restore_url": f"/projects/{project_id}/restore",
        "email_url":f"/email-templates?project_id={project_id}", 
        "document_url":f"/doc-templates?project_id={project_id}", 
        "return_url": "/projects", 
        "error": None,
    }

    try:
        result = await get_project(session, user.roles, user.id, project_id)

        query = StageQueryDTO(sort=sort, limit=limit, offset=offset)
        stage_result = await get_stage_list(session, user.roles, user.id, project_id, query)
        stage_template_result = await get_stage_template_list(
            session=session, creator_id=None, limit=1000, offset=0
        )

        context.update(
            {
                "name": result.get("name"),
                "description":  result.get("description"),
                "start_date":  result.get("start_date"),
                "end_date":  result.get("end_date"),
                "client_name":  result.get("client_name"),
                "client_email":  result.get("client_email"),
                "client_id": result.get("client_id"),
                "contract":  result.get("contract"),
                "manager":  result.get("manager"),
                "stages":  stage_result.get("items", []),
                "total": stage_result.get("total", 0),
                "limit": stage_result.get("limit", limit),
                "offset": stage_result.get("offset", offset),
                "stage_templates": stage_template_result.get("items", []),
                "is_archived": result.get("is_archived"),
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


@project_page_router.post("/projects/{project_id}/delete")
async def project_delete_page(
    request: Request,
    project_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("manager")
    ),
):

    context = {
        "request": request,
        "user": user,
        "project_id": project_id, 
        "detail_url": f"/projects/{project_id}",
        "return_url": "/projects",
        "error": None,
    }

    try:
        result = await archive_project(session, project_id, user.id)

        context.update(
            {
                "name": result.name,
                "message": "удалено",
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


@project_page_router.post("/projects/{project_id}/restore")
async def project_restore_page(
    request: Request,
    project_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("manager", "admin", "owner")
    ),
):

    context = {
        "request": request,
        "user": user,
        "project_id": project_id, 
        "detail_url": f"/projects/{project_id}",
        "error": None,
        "return_url": "/projects",
    }

    try:
        result = await restore_project(session, project_id, user.roles, user.id)

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


@project_page_router.get("/projects/{project_id}/files")
async def project_file_list_page(
    request: Request,
    project_id: int,
    sort: str | None = Query(default=None),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor"))
):
    context = {
        "request": request,
        "user": user,
        "files": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
        "sort": sort,
        "project_id": project_id,
        "error": None,
    }
    try:
        query = FileQueryDTO(sort=sort, limit=limit, offset=offset)
        result = await get_file_list(
            session=session, 
            user_id=user.id, 
            roles=user.roles, 
            entity_id=project_id,
            entity_type="project",
            query=query
        )

        context.update(
            {
                "files": result.get("items", []),
                "total": result.get("total", 0),
                "limit": result.get("limit", limit),
                "offset": result.get("offset", offset),
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="project/file_list.html",
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


@project_page_router.post("/projects/{project_id}/files/upload")
async def project_upload_page(
    request: Request,
    project_id: int,
    files: list[UploadFile] = File(...),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor")
    ),
):

    context = {
        "request": request,
        "user": user,
        "project_id": project_id, 
        "detail_url": f"/projects/{project_id}",
        "error": None,
    }

    try:
        uploaded_files = await upload_file(
            session=session, 
            user_id=user.id, 
            roles=user.roles,
            files=files, 
            entity_id=project_id,
            entity_type="project"
        )
    
        return RedirectResponse(
            url=f"/projects/{project_id}",
            status_code=303
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


@project_page_router.get("/projects/{id}/edit")
async def edit_project_page(
    request: Request,
    id: int,
    company_id: int | None = Query(None),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager")
    ),
):
    context = {
        "request": request,
        "user": user,
        "edit_url": f"/projects/{id}/edit",
        "error": None,
        "project_id": id,
        "return_url": "/projects",
    }

    try:
        result = await get_project(session, user.roles, user.id, id)

        companies = await get_company_list(
            session=session, 
            roles=user.roles, 
            requester_id=user.id, 
            query=CompanyQueryDTO(client_id=result.get("client_id"))
        )

        contracts = await get_contract_list(
            session=session,
            roles=user.roles,
            requester_id=user.id, 
            query=ContractQueryDTO(
                scope="mine",
                limit=1000,
                company_id=company_id,
            ),
        )

        context["template"] = result
        context["companies"] = companies.get("items", [])
        context["contracts"] = contracts.get("items", [])
        context["selected_company_id"] = company_id

        return templates.TemplateResponse(
            request=request,
            name="project/edit.html",
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


@project_page_router.post("/projects/{project_id}/edit")
async def project_template(
    request: Request,
    project_id: int,
    name: str = Form(None),
    description: str = Form(None),
    start_date: datetime = Form(None),
    end_date: datetime = Form(None),
    contract_id: int = Form(None),
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
        "edit_url": f"/projects/{project_id}/edit",
        "return_url": "/projects",
        "project_id": project_id,
        "error": None,
    }

    try:
        data = {
            "name": name,
            "description": description,
            "start_date": start_date,
            "end_date": end_date,      
        }

        if contract_id:
            data["contract_id"] = contract_id
 
        data = {k: v for k, v in data.items() if v not in ("", None)} 
        item = ProjectPatchRequest(**data) 

        result = await change_project(session, user.roles, user.id, project_id, item)

        context["template"] = result

        return RedirectResponse(
            url=f"/projects/{project_id}",
            status_code=303,
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