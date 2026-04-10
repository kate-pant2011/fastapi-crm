from fastapi import APIRouter, HTTPException, Depends, Query
from app.config.config import ApplicationException
from app.config.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import require_roles, UserDTO
from dataclasses import dataclass
from app.services.email_log import get_email_log_list, get_email_log
from app.schemas.email_log import EmailLogList, EmailLogItem
from app.models.email_log import EmailLogStatus
from enum import Enum

email_log_router = APIRouter()

class ScopeEnum(str, Enum):
    MINE = "mine"

@dataclass
class QueryDTO:
    sort: str | None
    limit: int
    offset: int
    to_email: int | None
    user_id: int | None
    from_email: str | None
    status: EmailLogStatus | None
    scope: str | None

@email_log_router.get("/email-logs", response_model=EmailLogList)
async def get_email_log_router(
    scope: ScopeEnum | None = Query(default=None, description="scope=mine, in case roles include admin + other"),
    to_email: str | None = Query(default=None),
    user_id: int | None = Query(default=None),
    from_email: str | None = Query(default=None),
    status: EmailLogStatus | None = Query(default=None),
    sort: str | None = Query(default=None, description="- stands for desc"),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        query = QueryDTO(
            sort=sort, limit=limit, 
            offset=offset, to_email=to_email, 
            user_id=user_id, scope=scope,
            from_email=from_email, status=status
        )
        return await get_email_log_list(
            session=session, roles=user.roles, user_id=user.id, query=query
        )

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=(f"{type(e).__name__} - {e}"))
    

@email_log_router.get("/email-logs/{id}", response_model=EmailLogItem)
async def get_email_log_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        return await get_email_log(session, user.roles, user.id, id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")