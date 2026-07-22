from fastapi import APIRouter, Depends, HTTPException, UploadFile,  Query, File, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.auth.dependencies import require_page_roles, UserDTO
from fastapi.responses import FileResponse
from app.config.config import ApplicationException
from app.auth.dependencies import require_roles, UserDTO
from app.schemas.common import BaseShortResponse, BaseListResponse
from app.schemas.branch import BranchItem, BranchCreationRequest, BranchPatchRequest
from app.services.branch import (
    create_branch,
    archive_branch,
    restore_branch,
    get_branch_list,
    get_branch,
    change_branch,
    delete_stamp,
    download_stamp
)
from app.config.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.routers.branch import BranchQueryDTO
from app.services.file import get_file_for_download, get_file_list, get_file, upload_file, delete_file

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
            name="branch/list.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="branch/list.html",
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
        "email_url":f"/email-form?branch_id={branch_id}", 
        "document_url":f"/document-form?branch_id={branch_id}", 
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
            request=request, name="branch/detail.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="branch/detail.html",
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
        "error": None,
    }

    try:
        result = await archive_branch(session, branch_id)

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
        "error": None,
    }

    try:
        result = await restore_branch(session, branch_id)

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