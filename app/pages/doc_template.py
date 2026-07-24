from fastapi import APIRouter, Depends, HTTPException, Query, Form, Request, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.responses import FileResponse
from app.auth.dependencies import require_page_roles, UserDTO
from typing import Literal
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.connection import get_db
from app.schemas.common import BaseShortResponse, BaseListResponse
from dataclasses import dataclass
from app.schemas.doc_template import (
    DocTemplateItem, 
    DocTemplateCreation, 
    DocTemplatePatchRequest, 
    DocTemplateDeleteResponse, 
    GeneratedDocResponse,
    RenderDocumentDTO
)
from app.services.doc_template import (
    get_doc_template_list, 
    get_doc_template, 
    create_doc_template, 
    change_doc_template, 
    delete_doc_template, 
    prepare_doc_template,
    render_doc_template,
)
from app.routers.doc_template import VariablesDTO
from urllib.parse import urlencode

doc_template_page_router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)

@doc_template_page_router.get("/doc-templates")
async def doc_template_list_page(
    request: Request,
    project_id: int | None = Query(None),
    client_id: int | None = Query(None),
    contract_id: int | None = Query(None),
    company_id: int | None = Query(None),
    stage_id: int | None = Query(None),
    branch_id: int | None = Query(None),
    scope: Literal["mine", "available"] | None = Query(
        default=None, 
        description="Filter: mine (only personal), available (shared + personal)"
    ),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor"))
):
    params = {
        "user_id": user.id,
        "project_id": project_id,
        "client_id": client_id,
        "contract_id": contract_id,
        "company_id": company_id,
        "stage_id": stage_id,
        "branch_id": branch_id,
    }

    query = urlencode(
        {k: v for k, v in params.items() if v is not None}
    )
    context = {
        "request": request,
        "user": user,
        "doc_templates": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
        "scope": scope,
        "error": None,
        "params": params,
        "query": query,
    }

    try:
        result = await get_doc_template_list(
            session=session, scope=scope, limit=limit, offset=offset, roles=user.roles, user_id=user.id
        )

        context.update(
            {
                "doc_templates": result.get("items", []),
                "total": result.get("total", 0),
                "limit": result.get("limit", limit),
                "offset": result.get("offset", offset),
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="doc_template/list.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, 
            name="doc_template/list.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="doc_template/list.html",
            context=context,
            status_code=500,
        )



@doc_template_page_router.post("/doc-templates/{doc_template_id}/delete")
async def doc_template_page_delete(
    request: Request,
    doc_template_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor"))
):
    context = {
        "request": request,
        "user": user,
        "doc_template_id": doc_template_id,
        "detail_url": f"/doc_templates/{doc_template_id}",
        "error": None,
    }
    try:
        result = await delete_doc_template(session, user.id, doc_template_id)

        context.update(
            {
                "deleted": "Удален без возможности восстановления",
                "name": "файла",
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
            name="archived_restored.html", 
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


@doc_template_page_router.get("/doc-templates/create")
async def create_doc_template_page(
    request: Request,
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor")
    ),
):
    context = {
        "request": request,
        "user": user,
        "create_url": "/doc-templates/create",
    }

    return templates.TemplateResponse(
        request=request,
        name="doc_template/create.html",
        context=context,
    )


@doc_template_page_router.post("/doc-templates/create")
async def create_doc_template_page(
    request: Request,
    name: str = Form(...),
    description: str | None = Form(None),
    is_public: bool | None = Form(False),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_page_roles("owner", "admin", "manager", "executor")),
):
    context = {
        "request": request,
        "user": user,
        "create_url": f"/doc_templates/create",
        "error": None,
    }

    try:
        data = DocTemplateCreation(
            name=name,
            description=description,
            is_public=is_public,
        )

        result = await create_doc_template(session, data, user.id, user.roles, file)

        context.update(
            {
                "id": result.id,
                "name": result.name,
                "form_data": {
                    "name": name,
                    "description": description,
                    "is_public": is_public,
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
            name="doc_templates/create.html", 
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


@doc_template_page_router.get("/doc-templates/{doc_template_id}")
async def doc_template_detail_page(
    request: Request,
    doc_template_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor")
    ),
):

    context = {
        "request": request,
        "user": user,
        "doc_template_id": doc_template_id,
        "edit_url": f"/doc-templates/{doc_template_id}/edit",
        "delete_url": f"/doc-templates/{doc_template_id}/delete",
        "error": None,
    }

    try:
        result = await get_doc_template(session, doc_template_id, user.roles, user.id)

        context.update(
            {
                "name": result.name,
                "description": result.description,
                "is_public": result.is_public,
                "variables": result.variables,
                "creator": result.creator,
                "file": result.file
            }

        )
        return templates.TemplateResponse(
            request=request,
            name="doc_template/detail.html",
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


@doc_template_page_router.get("/doc-templates/{id}/edit")
async def edit_doc_template_page(
    request: Request,
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles(
            "owner",
            "admin",
            "manager",
            "executor",
        )
    ),
):
    context = {
        "request": request,
        "user": user,
        "edit_url": f"/doc-templates/{id}/edit",
        "error": None,
    }

    try:
        result = await get_doc_template(
            session,
            id,
            user.roles,
            user.id,
        )

        context["template"] = result

        return templates.TemplateResponse(
            request=request,
            name="doc_template/edit.html",
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


@doc_template_page_router.post("/doc-templates/{id}/edit")
async def edit_doc_template(
    request: Request,
    id: int,
    description: str | None = Form(None),
    is_public: bool = Form(False),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles(
            "owner", "admin", "manager","executor",
        )
    ),
):
    context = {
        "request": request,
        "user": user,
        "edit_url": f"/doc-templates/{id}/edit",
        "error": None,
    }

    try:
        data = DocTemplatePatchRequest(
            description=description,
            is_public=is_public,
        )

        result = await change_doc_template(
            session=session,
            item=data,
            user_id=user.id,
            template_id=id,
        )

        context["template"] = result

        return RedirectResponse(
            url=f"/doc-templates/{id}",
            status_code=303,
        )

    except ApplicationException as e:
        context["error"] = e.name

        try:
            context["template"] = await get_doc_template(
                session, id, user.roles, user.id,
            )
        except Exception:
            pass

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


from urllib.parse import urlencode

@doc_template_page_router.get("/doc-template/{id}/form")
async def document_create_page(
    request: Request,
    id: int,
    project_id: int | None = Query(None),
    client_id: int | None = Query(None),
    contract_id: int | None = Query(None),
    company_id: int | None = Query(None),
    stage_id: int | None = Query(None),
    branch_id: int | None = Query(None),
    user: UserDTO = Depends(
        require_page_roles(
            "owner", "admin", "manager", "executor",
        )
    ),
):
    params = {
        "user_id": user.id,
        "project_id": project_id,
        "client_id": client_id,
        "contract_id": contract_id,
        "company_id": company_id,
        "stage_id": stage_id,
        "branch_id": branch_id,
    }

    query = urlencode(
        {k: v for k, v in params.items() if v is not None}
    )

    return templates.TemplateResponse(
        request=request,
        name="document/create.html",
        context={
            "request": request,
            "user": user,
            "template_id": id,
            "prepare_url": f"/page/doc-template/{id}/prepare?{query}",
            "render_url": f"/page/doc-template/{id}/render",
        },
    )


@doc_template_page_router.post("/page/doc-template/{id}/prepare")
async def prepare_doc_template_page(
    id: int,
    project_id: int | None = Query(None),
    client_id: int | None = Query(None),
    contract_id: int | None = Query(None),
    company_id: int | None = Query(None),
    stage_id: int | None = Query(None),
    branch_id: int | None = Query(None),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles(
            "owner", "admin", "manager", "executor",
        )
    ),
):
    query = VariablesDTO(
        project_id=project_id,
        client_id=client_id,
        contract_id=contract_id,
        company_id=company_id,
        stage_id=stage_id,
        user_id=user.id,        # всегда берем из токена
        branch_id=branch_id,
    )

    return await prepare_doc_template(
        session=session,
        user_id=user.id,
        roles=user.roles,
        template_id=id,
        query=query,
    )


@doc_template_page_router.post("/page/doc-template/{id}/render")
async def render_doc_template_page(
    id: int,
    data: RenderDocumentDTO,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles(
            "owner",
            "admin",
            "manager",
            "executor",
        )
    ),
):
    return await render_doc_template(
        session=session,
        user_id=user.id,
        roles=user.roles,
        template_id=id,
        data=data,
    )