from fastapi import APIRouter, Depends, HTTPException, Query, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.auth.dependencies import require_page_roles, UserDTO
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.generated_doc import get_generated_docs, send_generated_doc, convert_word_to_pdf
from app.config.config import ApplicationException
from app.config.connection import get_db
from dataclasses import dataclass
from app.schemas.generated_doc import GeneratedListResponse, GeneratedDocSend, GeneratedItem
from app.email.schemas import EmailStatusResponse
from app.schemas.doc_template import GeneratedDocResponse
from app.routers.generated_doc import DocsQueryDTO

generated_doc_page_router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)

@generated_doc_page_router.get("/documents")
async def generated_doc_list_page(
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
        "documents": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
        "error": None,
    }
    try:
        query = DocsQueryDTO(limit=limit, offset=offset)
        result = await get_generated_docs(
            session=session, 
            user_id=user.id, 
            query=query
        )

        context.update(
            {
                "documents": result.items,
                "total": result.total,
                "limit": result.limit,
                "offset": result.offset,
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="generated_doc/list.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, 
            name="generated_doc/list.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="generated_doc/list.html",
            context=context,
            status_code=500,
        )


@generated_doc_page_router.post("/generated-docs/{doc_id}/word-to-pdf")
async def convert_word_to_pdf_page(
    request: Request,
    doc_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor")
    ),
):
    try:
        result = await convert_word_to_pdf(
            session=session, 
            user_id=user.id, 
            generated_doc_id=doc_id,
        )
        
        return RedirectResponse(
            url=f"/documents",
            status_code=303
        )
        
    except ApplicationException as e:
        context = {
            "request": request,
            "user": user,
            "doc_id": doc_id,
            "error": e.name,
        }
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context=context,
            status_code=e.code,
        )
        
    except Exception as e:
        context = {
            "request": request,
            "user": user,
            "doc_id": doc_id,
            "error": f"{type(e).__name__} - {e}",
        }
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context=context,
            status_code=500,
        )