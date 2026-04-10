from fastapi import APIRouter, HTTPException, Depends, Form, File, UploadFile, Query
from typing import Literal
from app.config.config import ApplicationException
from app.config.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import require_roles, UserDTO
from .service import add_email_user, send_email_service, get_email_list, get_email, change_email, delete_email
from .schemas import (
    EmailShortResponse, EmailPostRequest, EmailStatusResponse, EmailListResponse, EmailItem, EmailPatchRequest
)


email_router = APIRouter()

@email_router.post("/email-account", response_model=EmailShortResponse)
async def add_email_router(
    items: EmailPostRequest, 
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin")),
):
    try: 
        return await add_email_user(session, items, user.id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail={"message": e.name, "payload": e.payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@email_router.get("/email-account", response_model=EmailListResponse)
async def get_email_list_router(
    session: AsyncSession = Depends(get_db),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    scope: Literal["mine", "available"] | None = Query(
        default=None, 
        description="Filter emails: mine (only personal), available (shared + personal)"
    ),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try: 
        return await get_email_list(session, limit, offset, user.id, user.roles, scope)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@email_router.get("/email-account/{id}", response_model=EmailItem)
async def get_email_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin")),
):
    try: 
        return await get_email(session, id)
    
    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail={"message": e.name, "payload": e.payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")
    

@email_router.patch("/email-account/{id}", response_model=EmailItem)
async def change_email_router(
    id: int,
    item:EmailPatchRequest,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin")),
):
    try: 
        return await change_email(session, item, id, user.id)
    
    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail={"message": e.name, "payload": e.payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


@email_router.delete("/email-account/{id}", response_model=EmailStatusResponse)
async def delete_email_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin")),
):
    try: 
        return await delete_email(session, id, user.id, user.roles)
    
    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail={"message": e.name, "payload": e.payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")



@email_router.post("/email", response_model=EmailStatusResponse)
async def send_email_router(
    files: list[UploadFile] | None = File(None),
    email_id: int = Form(...),
    to: str = Form(...),
    cc: str = Form(None),
    bcc: str = Form(None),
    subject: str = Form(None),
    body: str = Form(None),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try: 
        return await send_email_service(
            session, 
            files,
            email_id,
            to,
            cc,
            bcc,
            subject,
            body,
            user.id,
        )
    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail={"message": e.name, "payload": e.payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")
    

