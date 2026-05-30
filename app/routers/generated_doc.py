from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.generated_doc import get_generated_docs, send_generated_doc
from app.config.config import ApplicationException
from app.auth.dependencies import require_roles, UserDTO
from app.config.connection import get_db
from dataclasses import dataclass
from app.schemas.generated_doc import GeneratedListResponse, GeneratedDocCreation
from app.email.schemas import EmailStatusResponse

generated_doc_router = APIRouter()

@dataclass
class QueryDTO:
    sort: str | None
    limit: int
    offset: int



@generated_doc_router.get("/generated-docs", response_model=GeneratedListResponse)
async def get_generated_docs_router(
    sort: str | None = Query(default=None, description="- stands for desc"),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        query = QueryDTO(sort=sort, limit=limit, offset=offset)
        docs = await get_generated_docs(
            session=session, 
            user_id=user.id, 
            query=query
        )
        return docs

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")
    

@generated_doc_router.post("/generated-docs/{id}/send", response_model=EmailStatusResponse)
async def send_generated_docs_router(
    id: int,
    item: GeneratedDocCreation, 
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        docs = await send_generated_doc(
            session=session, 
            user_id=user.id, 
            generated_doc_id=id,
            item=item
        )
        return docs

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")