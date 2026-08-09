from fastapi import APIRouter, Depends, HTTPException, Query, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.auth.dependencies import require_page_roles, UserDTO
from typing import Literal
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.connection import get_db
from app.schemas.common import BaseShortResponse, BaseListResponse
from dataclasses import dataclass
from app.schemas.email_template import (
    EmailTemplateItem, 
    EmailTemplateCreation, 
    EmailTemplatePatchRequest, 
    EmailTemplateDeleteResponse, 
    EmailTemplateShortItem,
    EmailRenderDTO
)
from app.services.email_template import (
    get_email_template_list, 
    get_email_template, 
    create_email_template, 
    change_email_template, 
    delete_email_template, 
    render_email_template,
)
from app.services.stage_template import get_stage_template_list
from app.routers.email_template import VariablesDTO
from urllib.parse import urlencode
import traceback

email_template_page_router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)

@email_template_page_router.get("/email-templates")
async def email_template_list_page(
    request: Request,
    generated_id: int | None = Query(None),
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
        "generated_id": generated_id,
    }

    query = urlencode(
        {k: v for k, v in params.items() if v is not None}
    )
    context = {
        "request": request,
        "user": user,
        "email_templates": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
        "scope": scope,
        "query": query,
        "error": None,
    }
    try:
        result = await get_email_template_list(
            session=session, scope=scope, limit=limit, offset=offset, roles=user.roles, user_id=user.id
        )

        context.update(
            {
                "email_templates": result.get("items", []),
                "total": result.get("total", 0),
                "limit": result.get("limit", limit),
                "offset": result.get("offset", offset),
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="email_template/list.html",
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


@email_template_page_router.get("/email-templates/create")
async def create_email_template_page_(
    request: Request,
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor")
    ),
):
    context = {
        "request": request,
        "user": user,
        "create_url": "/email-templates/create",
    }

    return templates.TemplateResponse(
        request=request,
        name="email_template/create.html",
        context=context,
    )


@email_template_page_router.post("/email-templates/create")
async def create_email_template_page(
    request: Request,
    name: str = Form(...),
    subject_content: str | None = Form(None),
    body_content: str | None = Form(None),
    from_emails: str | None = Form(None),
    is_public: bool | None = Form(False),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_page_roles("owner", "admin", "manager", "executor")),
):
    context = {
        "request": request,
        "user": user,
        "create_url": f"/email-templates/create",
        "return_url": "/email-templates",
        "error": None,
    }

    if from_emails:
        if from_emails[-1] == ",":
            context["error"] = "Нельзя заканчивать список запятой"
            return templates.TemplateResponse(
                request=request, 
                name="error.html", 
                context=context,
                status_code=400,
            )
        elif "," in from_emails:
            from_emails = from_emails.split(",")
        else:
            from_emails = [from_emails]

    try:
        data = EmailTemplateCreation(
            name=name,
            subject_content=subject_content,
            body_content=body_content,
            from_emails=from_emails,
            is_public=is_public,
        )

        result = await create_email_template(session, data, user.id)

        context.update(
            {
                "id": result.id,
                "name": result.name,
                "form_data": {
                    "name": name,
                    "subject_content": subject_content,
                    "body_content": body_content,
                    "from_emails": from_emails,
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


@email_template_page_router.get("/email-templates/{email_template_id}")
async def email_template_detail_page(
    request: Request,
    email_template_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor")
    ),
):

    context = {
        "request": request,
        "user": user,
        "email_template_id": email_template_id,
        "edit_url": f"/email-templates/{email_template_id}/edit",
        "delete_url": f"/email-templates/{email_template_id}/delete",
        "return_url": "/email-templates",
        "error": None,
    }

    try:
        result = await get_email_template(session, email_template_id, user.roles, user.id)

        context.update(
            {
                "name": result.name,
                "subject_content": result.subject_content,
                "body_content": result.body_content,
                "is_public": result.is_public,
                "creator": result.creator
            }
        )

        return templates.TemplateResponse(
            request=request,
            name="email_template/detail.html",
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


@email_template_page_router.post("/email-templates/{email_template_id}/delete")
async def email_template_delete_page(
    request: Request,
    email_template_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor")
    ),
):

    context = {
        "request": request,
        "user": user,
        "email_template_id": email_template_id,
        "detail_url": f"/email-templates/{email_template_id}",
        "return_url": "/email-templates",
        "error": None,
    } 

    try:
        result = await delete_email_template(session, user.id, user.roles, email_template_id)

        context.update(
            {
                "name": result.get("name"),
                "message": "удаление без возможности восстановления",
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


@email_template_page_router.get("/email-template/{id}/form")
async def email_form_page(
    request: Request,
    id: int,
    project_id: int | None = Query(None),
    client_id: int | None = Query(None),
    contract_id: int | None = Query(None),
    company_id: int | None = Query(None),
    stage_id: int | None = Query(None),
    branch_id: int | None = Query(None),
    generated_id: int | None = Query(None),
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
        "generated_id": generated_id,
    }

    query = urlencode(
        {k: v for k, v in params.items() if v is not None}
    )

    return templates.TemplateResponse(
        request=request,
        name="email_template/render.html",
        context={
            "request": request,
            "user": user,
            "template_id": id,
            "render_url": f"/page/email-template/{id}/render?{query}",
            "generated_id": generated_id or None,
        },
    )


@email_template_page_router.post("/page/email-template/{id}/render")
async def render_email_template_page(
    request: Request, 
    id: int,
    project_id: int | None = Query(None),
    client_id: int | None = Query(None),
    contract_id: int | None = Query(None),
    company_id: int | None = Query(None),
    stage_id: int | None = Query(None),
    branch_id: int | None = Query(None),
    generated_id: int | None = Query(None),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_page_roles(
            "owner", "admin", "manager", "executor",
        )
    ),
):
    context = {
        "request": request,
        "user": user,
        "error": None,
    } 
    try:
        query = VariablesDTO(
            project_id=project_id,
            client_id=client_id,
            contract_id=contract_id,
            company_id=company_id,
            stage_id=stage_id,
            branch_id=branch_id,
            user_id=user.id,
            generated_id=generated_id
        )

        result = await render_email_template(session, user.id, user.roles, id, query)
        return result

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


@email_template_page_router.get("/email-templates/{id}/edit")
async def edit_doc_template_page(
    request: Request,
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles(
            "owner", "admin", "manager", "executor",
        )
    ),
):
    context = {
        "request": request,
        "user": user,
        "edit_url": f"/email-templates/{id}/edit",
        "error": None,
        "return_url": "/email-templates",
    }

    try:
        result = await get_email_template(
            session,
            id,
            user.roles,
            user.id, 
        )

        context["template"] = result

        return templates.TemplateResponse(
            request=request,
            name="email_template/edit.html",
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


@email_template_page_router.post("/email-templates/{id}/edit")
async def edit_doc_template(
    request: Request,
    id: int,
    subject_content: str | None = Form(None),
    body_content: str | None = Form(None),
    from_emails: list[str] | None = Form(None),
    is_public: bool | None = Form(False),
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
        "edit_url": f"/email-templates/{id}/edit",
        "return_url": "/email-templates",
        "error": None,
    }

    if from_emails:
        if from_emails[-1] == ",":
            context["error"] = "Нельзя заканчивать список запятой"
            return templates.TemplateResponse(
                request=request, 
                name="error.html", 
                context=context,
                status_code=400,
            )
        elif "," in from_emails:
            from_emails = from_emails.split(",")
        else:
            from_emails = [from_emails]
        
    try:
        data = EmailTemplatePatchRequest(
            subject_content=subject_content,
            is_public=is_public,
            body_content=body_content,
            from_emails=from_emails

        )

        result = await change_email_template(
            session=session,
            item=data,
            user_id=user.id,
            template_id=id,
        )

        context["template"] = result

        return RedirectResponse(
            url=f"/email-templates/{id}",
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