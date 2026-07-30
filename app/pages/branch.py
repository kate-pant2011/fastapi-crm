from fastapi import APIRouter, Depends, HTTPException, UploadFile,  Query, File, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.auth.dependencies import require_page_roles, UserDTO
from app.schemas.branch import BranchPatchRequest
from app.config.config import ApplicationException
from app.services.branch import (
    archive_branch,
    restore_branch,
    get_branch_list,
    get_branch,
    create_branch,
    change_branch
)
from app.config.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.routers.branch import BranchQueryDTO
from app.services.file import upload_file
from .common import organization_patch_form

branch_page_router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)

@branch_page_router.get("/branches")
async def branch_list_page(
    request: Request,
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
        "branches": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
        "sort": sort,
        "error": None,
    }
    try:
        query = BranchQueryDTO(sort=sort, limit=limit, offset=offset)
        result = await get_branch_list(session, query)

        context.update(
            {
                "branches": result.get("items", []),
                "total": result.get("total", 0),
                "limit": result.get("limit", limit),
                "offset": result.get("offset", offset),
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="branch/list.html",
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


@branch_page_router.get("/branches/create")
async def create_branch_page_(
    request: Request,
    user: UserDTO = Depends(
        require_page_roles("owner", "admin")
    ),
):
    try:
        context = {
            "request": request,
            "user": user,
            "create_url": "/branches/create",
        }

        return templates.TemplateResponse(
            request=request,
            name="branch/create.html",
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

@branch_page_router.post("/branches/create")
async def create_branch_page(
    request: Request,
    name: str = Form(...),
    inn: str = Form(...),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_page_roles("owner", "admin")),
):
    context = {
        "request": request,
        "user": user,
        "create_url": "/branches/create",
        "return_url": "/branches",
        "error": None,
    }

    try:
        result = await create_branch(session, inn, name)

        context.update(
            {
                "id": result.id,
                "name": result.name,
                "form_data": {
                    "name": name,
                    "inn": inn,
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

    
@branch_page_router.get("/branches/{branch_id}")
async def branch_detail_page(
    request: Request,
    branch_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor")
    ),
):

    context = {
        "request": request,
        "user": user,
        "branch_id": branch_id,
        "edit_url": f"/branches/{branch_id}/edit",
        "delete_url": f"/branches/{branch_id}/delete",
        "restore_url": f"/branches/{branch_id}/restore",
        "email_url":f"/email-templates?branch_id={branch_id}", 
        "document_url":f"/doc-templates?branch_id={branch_id}", 
        "return_url":"/branches",
        "error": None,
    }

    try:
        result = await get_branch(session, branch_id)

        context.update(
            {
                "name": result.name,
                "inn": result.inn,
                "users": result.users,
                "stamp_file_id": result.stamp_file_id,
                "stamp_width_mm": result.stamp_width_mm,
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
                "is_archived": result.is_archived,
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="branch/detail.html",
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


@branch_page_router.post("/branches/{branch_id}/delete")
async def branch_delete_page(
    request: Request,
    branch_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin")
    ),
):

    context = {
        "request": request,
        "user": user,
        "branch_id": branch_id, 
        "detail_url": f"/branches/{branch_id}",
        "return_url":f"/branches/{branch_id}",
        "error": None,
        "message": None
    }

    try:
        result = await archive_branch(session, branch_id)

        context.update(
            {
                "name": result.name,
                "message": "удаление"
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="archived_restored.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name
        context["return_url"] = "/branches"

        return templates.TemplateResponse(
            request=request, name="error.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"
        context["return_url"] = "/branches"

        return templates.TemplateResponse(
            request=request, 
            name="error.html",
            context=context,
            status_code=500,
        )


@branch_page_router.post("/branches/{branch_id}/restore")
async def branch_restore_page(
    request: Request,
    branch_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin")
    ),
):

    context = {
        "request": request,
        "user": user,
        "branch_id": branch_id, 
        "detail_url": f"/branches/{branch_id}",
        "return_url":f"/branches/{branch_id}",
        "error": None,
    }

    try:
        result = await restore_branch(session, branch_id)

        context.update(
            {
                "name": result.name,
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
        context["return_url"] = "/branches"

        return templates.TemplateResponse(
            request=request, name="error.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"
        context["return_url"] = "/branches"

        return templates.TemplateResponse(
            request=request, 
            name="error.html",
            context=context,
            status_code=500,
        )


@branch_page_router.post("/branches/{branch_id}/files/upload")
async def branch_upload_page(
    request: Request,
    branch_id: int,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor")
    ),
):

    context = {
        "request": request,
        "user": user,
        "branch_id": branch_id, 
        "detail_url": f"/branches/{branch_id}",
        "return_url":"/branches",
        "error": None,
    }

    try:
        uploaded_files = await upload_file(
            session=session, 
            user_id=user.id, 
            roles=user.roles,
            files=[file], 
            entity_id=branch_id,
            entity_type="branch"
        )
    
        return RedirectResponse(
            url=f"/branches/{branch_id}",
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


@branch_page_router.get("/branches/{id}/edit")
async def edit_branch_page(
    request: Request,
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles(
            "owner", "admin", 
        )
    ),
):
    context = {
        "request": request,
        "user": user,
        "edit_url": f"/branches/{id}/edit",
        "error": None,
        "return_url": "/branches",
    }

    try:
        result = await get_branch(session, id)

        context["template"] = result

        return templates.TemplateResponse(
            request=request,
            name="branch/edit.html",
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


@branch_page_router.post("/branches/{id}/edit")
async def branch_template(
    request: Request,
    id: int,
    item: BranchPatchRequest = Depends(organization_patch_form),
    stamp_width_mm: int | None = Form(None),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles(
            "owner", "admin", 
        )
    ),
):
    context = {
        "request": request,
        "user": user,
        "edit_url": f"/branches/{id}/edit",
        "return_url": "/branches",
        "error": None,
    }
    
    try:
        data = item.model_dump(exclude_none=True)

        if stamp_width_mm is not None:
            data["stamp_width_mm"] = stamp_width_mm

        branch_item = BranchPatchRequest(**data)

        result = await change_branch(
            session=session, branch_id=id, item=branch_item,
        )

        context["template"] = result

        return RedirectResponse(
            url=f"/branches/{id}",
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


