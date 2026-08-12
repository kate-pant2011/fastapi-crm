from fastapi import APIRouter, Depends, HTTPException, Query, Form, Request, File, Form
from fastapi.templating import Jinja2Templates
from app.auth.dependencies import require_page_roles, UserDTO
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import FileResponse
from app.services.file import get_file_for_download, get_file_list, get_file, upload_file, delete_file
from app.config.config import ApplicationException
from app.auth.dependencies import require_roles, UserDTO
from app.config.connection import get_db
from app.schemas.file import FileDeleteResponse, FileItem
from app.schemas.common import BaseShortResponse, BaseListResponse
from dataclasses import dataclass


file_page_router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)

@file_page_router.get("/files/{file_id}")
async def file_page(
    request: Request,
    file_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor"))
):
    context = {
        "request": request,
        "user": user,
        "file_id": file_id,
        "error": None,
    }
    try:
        result = await get_file(
            session=session, 
            user_id=user.id, 
            roles=user.roles, 
            file_id=file_id, 
        )

        context.update(
            {
                "id": result.id,
                "name": result.name,
                "size": result.size,
                "mime_type": result.mime_type,
                "creator": result.creator,
                "project": result.project,
                "client": result.client,

            }
        )

        return templates.TemplateResponse(
            request=request,
            name="file/detail.html",
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


@file_page_router.post("/files/{file_id}/delete")
async def file_page_delete(
    request: Request,
    file_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor"))
):
    context = {
        "request": request,
        "user": user,
        "file_id": file_id,
        "detail_url": f"/files/{file_id}",
        "error": None,
    }
    try:
        result = await delete_file(
            session=session, 
            user_id=user.id, 
            roles=user.roles, 
            file_id=file_id, 
        )

        context.update(
            {
                "message": "удаление без возможности восстановления",
                "name": "файл",
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


@file_page_router.post("/files/{file_id}/download")
async def file_page_download(
    request: Request,
    file_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor"))
):
    context = {
        "request": request,
        "user": user,
        "file_id": file_id,
        "detail_url": f"/files/{file_id}",
        "error": None,
    }
    try:
        file = await get_file_for_download(
            session=session, 
            user_id=user.id, 
            roles=user.roles, 
            file_id=file_id, 
        )
        
        return FileResponse(
            path=file.path, filename=file.name, media_type=file.mime_type
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