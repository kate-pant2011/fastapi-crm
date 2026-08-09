from fastapi import APIRouter, Depends, HTTPException, Query, Form, Request, File, Form, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.auth.dependencies import require_page_roles, UserDTO
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.connection import get_db
from app.schemas.common import BaseShortResponse, BaseListResponse
from app.schemas.client import ClientItem, ClientCreation, ClientPatchRequest
from app.services.client import (
    form_client_list,
    get_client,
    create_client,
    archive_client,
    restore_client,
    change_client,
)
from app.routers.client import ClientQueryDTO
from app.routers.user import get_user_list, QueryDTO
from typing import Literal
from app.services.file import get_file_for_download, get_file_list, get_file, upload_file, delete_file
from app.routers.file import FileQueryDTO

client_page_router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)


@client_page_router.get("/clients")
async def client_list_page(
    request: Request,
    scope: Literal["mine"] | None = Query(
        default=None, description="scope ignored if manager_id provided"
    ),
    manager_id: int | None = Query(default=None),
    sort: str | None = Query(default=None),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    is_archived: bool | None = Query(default=None),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager"))
):
    context = {
        "request": request,
        "user": user,
        "clients": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
        "is_archived": is_archived,
        "sort": sort,
        "manager_id": manager_id,
        "scope": scope,
        "error": None,
    }
    try:
        query = ClientQueryDTO(
            sort=sort,
            limit=limit,
            offset=offset,
            manager_id=manager_id,
            scope=scope,
            is_archived=is_archived
        )
        result = await form_client_list(
            session=session, roles=user.roles, requester_id=user.id, query=query
        )

        managers_result = await get_user_list(
            session=session, roles=user.roles, query=QueryDTO(
                role_name="manager", limit=1000
            )
        )

        context.update(
            {
                "clients": result.get("items", []),
                "total": result.get("total", 0),
                "limit": result.get("limit", limit),
                "offset": result.get("offset", offset),
                "managers": managers_result.get("items", [])
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="client/list.html",
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


@client_page_router.get("/clients/create")
async def create_client_page_(
    request: Request,
    user: UserDTO = Depends(
        require_page_roles("manager")
    ),
):
    context = {
        "request": request,
        "user": user,
        "create_url": "/clients/create",
    }
    try:
        return templates.TemplateResponse(
            request=request,
            name="client/create.html",
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

@client_page_router.post("/clients/create")
async def create_client_page(
    request: Request,
    name: str = Form(...),
    email: str = Form(None),
    telephone: str = Form(None),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_page_roles("manager")),
):
    context = {
        "request": request,
        "user": user,
        "create_url": "clients/create",
        "return_url": "/clients",
        "error": None,
    }

    if email:
        if email[-1] == ",":
            context["error"] = "Нельзя заканчивать список запятой"
            return templates.TemplateResponse(
                request=request, 
                name="error.html", 
                context=context,
                status_code=400,
            )
        elif "," in email:
            email = email.split(",")
        else:
            email = [email]

    if telephone:
        if telephone[-1] == ",":
            context["error"] = "Нельзя заканчивать список запятой"
            return templates.TemplateResponse(
                request=request, 
                name="error.html", 
                context=context,
                status_code=400,
            )
        elif "," in telephone:
            telephone = telephone.split(",")
        else:
            telephone = [telephone]

    data = ClientCreation(
        name=name, email=email, telephone=telephone
    )

    try:
        result = await create_client(session, data, user.id)

        context.update(
            {
                "id": result.id,
                "name": result.name,
                "form_data": {
                    "name": name,
                    "email": email,
                    "telephone": telephone
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
    

@client_page_router.get("/clients/{client_id}")
async def client_detail_page(
    request: Request,
    client_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager")
    ),
):

    context = {
        "request": request,
        "user": user,
        "client_id": client_id,
        "edit_url": f"/clients/{client_id}/edit",
        "delete_url": f"/clients/{client_id}/delete",
        "restore_url": f"/clients/{client_id}/restore",
        "email_url":f"/email-templates?client_id={client_id}", 
        "document_url":f"/doc-templates?client_id={client_id}", 
        "return_url":"/clients",
        "error": None,
    }

    try:
        result = await get_client(session, user.roles, user.id, client_id)

        context.update(
            {
                "name": result.name,
                "email": result.email,
                "telephone": result.telephone,
                "manager": result.manager,
                "projects": result.projects,
                "companies": result.companies,
                "is_archived": result.is_archived,
                "files_count": result.files_count
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="client/detail.html",
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


@client_page_router.post("/clients/{client_id}/delete")
async def client_delete_page(
    request: Request,
    client_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("manager")
    ),
):

    context = {
        "request": request,
        "user": user,
        "client_id": client_id, 
        "detail_url": f"/clients/{client_id}",
        "return_url":f"/clients/{client_id}",
        "error": None,
    }

    try:
        result = await archive_client(session, client_id, user.id)

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


@client_page_router.post("/clients/{client_id}/restore")
async def client_restore_page(
    request: Request,
    client_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager")
    ),
):

    context = {
        "request": request,
        "user": user,
        "client_id": client_id, 
        "detail_url": f"/clients/{client_id}",
        "return_url":f"/clients/{client_id}",
        "error": None,
    }

    try:
        result = await restore_client(session, client_id, user.roles, user.id)

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


@client_page_router.get("/clients/{client_id}/files")
async def client_file_list_page(
    request: Request,
    client_id: int,
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
        "files": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
        "sort": sort,
        "client_id": client_id,
        "return_url":"/clients",
        "error": None,
    }
    try:
        query = FileQueryDTO(sort=sort, limit=limit, offset=offset)
        result = await get_file_list(
            session=session, 
            user_id=user.id, 
            roles=user.roles, 
            entity_id=client_id,
            entity_type="client",
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
            name="client/file_list.html",
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


@client_page_router.post("/clients/{client_id}/files/upload")
async def client_upload_page(
    request: Request,
    client_id: int,
    files: list[UploadFile] = File(...),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager")
    ),
):

    context = {
        "request": request,
        "user": user,
        "client_id": client_id, 
        "detail_url": f"/clients/{client_id}",
        "return_url":"/clients",
        "error": None,
    }

    try:
        uploaded_files = await upload_file(
            session=session, 
            user_id=user.id, 
            roles=user.roles,
            files=files, 
            entity_id=client_id,
            entity_type="client"
        )
    
        return RedirectResponse(
            url=f"/clients/{client_id}",
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



@client_page_router.get("/clients/{id}/edit")
async def edit_user_page(
    request: Request,
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager")
    ),
):
    context = {
        "request": request,
        "user": user,
        "edit_url": f"/clients/{id}/edit",
        "error": None,
        "return_url": "/clients",
    }

    try:
        result = await get_client(session, user.roles, user.id, id)

        managers = await get_user_list(
            session=session,
            roles=user.roles,
            query=QueryDTO(
                role_name="manager",
                limit=1000,
            ),
        )

        context["template"] = result
        context["managers"] = managers.get("items", [])

        return templates.TemplateResponse(
            request=request,
            name="client/edit.html",
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


@client_page_router.post("/clients/{id}/edit")
async def user_template(
    request: Request,
    id: int,
    name: str = Form(None),
    email: str = Form(None),
    telephone: str = Form(None),
    manager_id: int = Form(None),
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
        "edit_url": f"/clients/{id}/edit",
        "return_url": "/clients",
        "error": None,
    }
    if email:
        if email[-1] == ",":
            context["error"] = "Нельзя заканчивать список запятой"
            return templates.TemplateResponse(
                request=request, 
                name="error.html", 
                context=context,
                status_code=400,
            )
        elif "," in email:
            email = email.split(",")
        else:
            email = [email]

    if telephone: 
        if telephone[-1] == ",":
            context["error"] = "Нельзя заканчивать список запятой"
            return templates.TemplateResponse(
                request=request, 
                name="error.html", 
                context=context,
                status_code=400,
            )
        elif "," in telephone:
            telephone = telephone.split(",")
        else:
            telephone = [telephone]

    try:
        data = {
            "name": name,
            "email": email,
            "telephone": telephone,      
        }

        if manager_id:
            data["manager_id"] = manager_id
 
        data = {k: v for k, v in data.items() if v not in ("", None)} 
        item = ClientPatchRequest(**data) 

        result = await change_client(session, user.roles, user.id, id, item)

        context["template"] = result

        return RedirectResponse(
            url=f"/clients/{id}",
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