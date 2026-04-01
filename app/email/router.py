from fastapi import APIRouter, HTTPException, Depends, Form, File, UploadFile
from app.config.config import ApplicationException
from app.config.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import require_roles, UserDTO
from .service import add_email_user, send_email_service
from .schemas import EmailPostResponse, EmailPostRequest, EmailLogResponse


email_router = APIRouter()

@email_router.post("/email-user", response_model=EmailPostResponse)
async def add_email_router(
    items: EmailPostRequest, 
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try: 
        return await add_email_user(session, items, user.id, user.roles)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail={"message": e.name, "payload": e.payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")

@email_router.post("/email", response_model=EmailLogResponse)
async def send_email_router(
    files: list[UploadFile] = File(defaul=[]),
    email_id: int = Form(...),
    to: str = Form(...),
    cc: str = Form(None),
    subject: str = Form(...),
    body: str = Form(...),
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
            subject,
            body,
            user.id
        )
    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail={"message": e.name, "payload": e.payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")