from fastapi import APIRouter, Depends, HTTPException, Query, Form, Request
from fastapi.templating import Jinja2Templates
from app.auth.dependencies import require_page_roles, UserDTO
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import UserDTO
from app.config.connection import get_db
from app.config.config import ApplicationException
from app.auth.dependencies import require_roles
from app.schemas.common import BaseShortResponse, BaseListResponse
from app.schemas.contractor import (
    ContractorItem,
    ContractorCreation,
    ContractorPatchRequest,
)
from app.services.contractor import (
    get_contractor_list,
    get_contractor,
    create_contractor,
    archive_contractor,
    restore_contractor,
    change_contractor,
)

contractor_page_router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)

@contractor_page_router.get("/contractors")
async def contractor_list_page(
    request: Request,
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor"))
):
    context = {
        "request": request,
        "user": user,
        "contractors": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
        "error": None,
    }
    try:
        result = await get_contractor_list(session, limit, offset)

        context.update(
            {
                "contractors": result.get("items", []),
                "total": result.get("total", 0),
                "limit": result.get("limit", limit),
                "offset": result.get("offset", offset),
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="contractor/list.html",
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


@contractor_page_router.get("/contractors/create")
async def create_contractor_page_(
    request: Request,
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor")
    ),
):
    context = {
        "request": request,
        "user": user,
        "create_url": "/contractors/create",
    }

    return templates.TemplateResponse(
        request=request,
        name="contractor/create.html",
        context=context,
    )


@contractor_page_router.post("/contractors/create")
async def create_contractor_page(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    email: str = Form(None),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_page_roles("owner", "admin", "manager", "executor")),
):
    context = {
        "request": request,
        "user": user,
        "create_url": "/contractors/create",
        "return_url": "/contractors",
        "error": None,
    }

    if "," in email:
        email = email.split(",")
    else:
        email = [email]

    try:
        data = ContractorCreation(
            name=name,
            email=email,
            description=description
        )

        result = await create_contractor(session, data)

        context.update(
            {
                "id": result.id,
                "name": result.name,
                "form_data": {
                    "name": name,
                    "email": email,
                    "description": description
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
    

@contractor_page_router.get("/contractors/{contractor_id}")
async def contractor_detail_page(
    request: Request,
    contractor_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor")
    ),
):

    context = {
        "request": request,
        "user": user,
        "contractor_id": contractor_id,
        "edit_url": f"/contractors/{contractor_id}/edit",
        "delete_url": f"/contractors/{contractor_id}/delete",
        "restore_url": f"/contractors/{contractor_id}/restore",
        "return_url": "/contractors",
        "error": None,
    }

    try:
        result = await get_contractor(session, contractor_id)

        context.update(
            {
                "name": result.name,
                "email": result.email,
                "description": result.description,
                "is_archived": result.is_archived,
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="contractor/detail.html",
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


@contractor_page_router.post("/contractors/{contractor_id}/delete")
async def contractor_delete_page(
    request: Request,
    contractor_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor")
    ),
):

    context = {
        "request": request,
        "user": user,
        "contractor_id": contractor_id,
        "detail_url": f"/contractors/{contractor_id}",
        "return_url": f"/contractors/{contractor_id}",
        "error": None,
    } 

    try:
        result = await archive_contractor(session, contractor_id)

        context.update(
            {
                "name": result.name,
                "id": result.id,
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


@contractor_page_router.post("/contractors/{contractor_id}/restore")
async def contractor_restore_page(
    request: Request,
    contractor_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor")
    ),
):

    context = {
        "request": request,
        "user": user,
        "contractor_id": contractor_id,
        "detail_url": f"/contractors/{contractor_id}",
        "return_url": f"/contractors/{contractor_id}",
        "error": None,
    } 

    try:
        result = await restore_contractor(session, contractor_id)

        context.update(
            {
                "name": result.name,
                "id": result.id,
                "message": "восстановление"
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


@contractor_page_router.get("/contractors/{id}/edit")
async def edit_contractor_page(
    request: Request,
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles(
            "owner", "admin", "manager", "executor"
        )
    ),
):
    context = {
        "request": request,
        "user": user,
        "edit_url": f"/contractors/{id}/edit",
        "error": None,
        "return_url": "/contractors",
    }

    try:
        result = await get_contractor(session, id)

        context["template"] = result

        return templates.TemplateResponse(
            request=request,
            name="contractor/edit.html",
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


@contractor_page_router.post("/contractors/{id}/edit")
async def contractor_template(
    request: Request,
    id: int,
    name: str = Form(...),
    description: str = Form(...),
    email: str = Form(None),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles(
            "owner", "admin", "manager", "executor"
        )
    ),
):
    context = {
        "request": request,
        "user": user,
        "edit_url": f"/contractors/{id}/edit",
        "return_url": "/contractors",
        "error": None,
    }

    if email[-1] == ",":
       email = [email[ 0:-1]]
    elif "," in email:
        email = email.split(",")
    else:
        email = [email]
        
    try:
        data = ContractorPatchRequest(
            name=name,
            email=email,
            description=description
        )

        result = await change_contractor(
            session=session,
            contractor_id=id,
            item=data,

        )

        context["template"] = result

        return RedirectResponse(
            url=f"/contractors/{id}",
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