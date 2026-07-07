from fastapi import APIRouter, Depends, HTTPException, UploadFile,  Query, File
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import FileResponse
from app.services.file import get_file_for_download, get_file_list, get_file, upload_file, delete_file
from app.config.config import ApplicationException
from app.auth.dependencies import require_roles, UserDTO
from app.config.connection import get_db
from app.schemas.file import FileDeleteResponse, FileItem
from app.schemas.common import BaseShortResponse, BaseListResponse
from dataclasses import dataclass

file_router = APIRouter()

@dataclass
class QueryDTO:
    sort: str | None
    limit: int
    offset: int


@file_router.get("/project/{id}/files", response_model=BaseListResponse)
async def get_files_project(
    id: int,
    sort: str | None = Query(default=None, description="- stands for desc"),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        query = QueryDTO(sort=sort, limit=limit, offset=offset)
        files = await get_file_list(
            session=session, 
            user_id=user.id, 
            roles=user.roles, 
            entity_id=id,
            entity_type="project",
            query=query
        )
        return files

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")
    

@file_router.get("/client/{id}/files", response_model=BaseListResponse)
async def get_files_client(
    id: int,
    sort: str | None = Query(default=None, description="- stands for desc"),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        query = QueryDTO(sort=sort, limit=limit, offset=offset)
        files = await get_file_list(
            session=session, 
            user_id=user.id, 
            roles=user.roles, 
            entity_id=id,
            entity_type="client",
            query=query
        )
        return files

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")
    
@file_router.get("/files/{file_id}", response_model=FileItem)
async def get_file_project(
    file_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        result = await get_file(
            session=session, 
            user_id=user.id, 
            roles=user.roles, 
            file_id=file_id, 
        )
        return result

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@file_router.post("/project/{id}/files", response_model=list[BaseShortResponse])
async def upload_file_project(
    id: int,
    files: list[UploadFile] = File(...),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        uploaded_files = await upload_file(
            session=session, 
            user_id=user.id, 
            roles=user.roles,
            files=files, 
            entity_id=id,
            entity_type="project"
        )
        return uploaded_files

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")

@file_router.post("/client/{id}/files", response_model=list[BaseShortResponse])
async def upload_file_client(
    id: int,
    files: list[UploadFile] = File(...),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        uploaded_files = await upload_file(
            session=session, 
            user_id=user.id, 
            roles=user.roles,
            files=files, 
            entity_id=id,
            entity_type="client"
        )
        return uploaded_files

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")

@file_router.post("/branch/{id}/files", response_model=list[BaseShortResponse])
async def upload_file_client(
    id: int,
    files: list[UploadFile] = File(...),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        uploaded_files = await upload_file(
            session=session, 
            user_id=user.id, 
            roles=user.roles,
            files=files, 
            entity_id=id,
            entity_type="branch"
        )
        return uploaded_files

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@file_router.get("/files/{file_id}/download")
async def download_file_router(
    file_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        file = await get_file_for_download(
            session=session, 
            user_id=user.id, 
            roles=user.roles, 
            file_id=file_id, 
        )
        return FileResponse(path=file.path, filename=file.name, media_type=file.mime_type) 

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")
    

@file_router.delete("/files/{file_id}", response_model=FileDeleteResponse)
async def delete_file_router(
    file_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        result = await delete_file(
            session=session, 
            user_id=user.id, 
            roles=user.roles, 
            file_id=file_id, 
        )
        return {"deleted": result}

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")
    

    
