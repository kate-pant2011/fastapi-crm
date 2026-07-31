from fastapi import APIRouter, Depends, HTTPException, Query, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import require_page_roles
from app.auth.dependencies import UserDTO
from app.config.connection import get_db
from app.schemas.common import BaseShortResponse, BaseListResponse
from app.schemas.assignment import (
    AssignmentItem,
    AssignmentCreation,
    AssignmentPatchRequest,
)
from app.services.assignment import (
    form_assignment_list,
    get_assignment, 
    get_assignments_me,
    create_assignment, 
    change_assignment, 
    delete_assignment
)
from dataclasses import dataclass
from typing import Literal
from app.routers.user import get_user_list, QueryDTO
from app.services.contractor import get_contractor_list
from app.routers.assignment import AssignmentQueryDTO
from datetime import datetime

assignment_page_router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)

@assignment_page_router.get("/assignments")
async def assignment_list_page(
    request: Request,
    is_done: bool | None = Query(default=None),
    scope: Literal["users", "contractors"] | None = Query(
        default=None, 
        description="Filter: either users or contractors list"
    ),
    sort: str | None = Query(default=None),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin")
    ),
):
    context = {
        "request": request,
        "user": user,
        "assignments": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
        "sort": sort,
        "is_done": is_done,
        "scope": scope,
        "error": None,
    }
    try:
        query = AssignmentQueryDTO(
            sort=sort,
            limit=limit,
            offset=offset,
            is_done=is_done,
            scope=scope
        )
        result = await form_assignment_list(session=session, query=query)

        context.update(
            {
                "assignments": result.get("items", []),
                "total": result.get("total", 0),
                "limit": result.get("limit", limit),
                "offset": result.get("offset", offset),
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="assignment/list.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, 
            name="assignment/list.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="assignment/list.html",
            context=context,
            status_code=500,
        )

@assignment_page_router.get("/assignments/create")
async def create_assignment_page_(
    request: Request,
    stage_id: int = Query(),
    stage_name: str = Query(),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("manager")
    ),
):
    context = {
        "request": request,
        "user": user,
        "create_url": f"/assignments/create?stage_id={stage_id}",
        "stage_id": stage_id,
        "stage_name": stage_name,
        "error": None,
    }
    try:
        users = await get_user_list(
            session=session, roles=user.roles, query=QueryDTO(
                role_name="executor", limit=1000
            )
        )
        contractors = await get_contractor_list(session, limit=1000, offset=0)

        context.update(
            {
                "users":  users.get("items", []),
                "contractors": contractors.get("items", [])
            }
        )

        return templates.TemplateResponse(
            request=request,
            name="assignment/create.html",
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

@assignment_page_router.post("/assignments/create")
async def create_assignment_page(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    stage_id: int = Form(...),
    user_id: int = Form(None),
    contractor_id: int = Form(None),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_page_roles("manager")),
):
    context = {
        "request": request,
        "user": user,
        "create_url": "assignments/create",
        "error": None,
        "stage_id": stage_id
    }

    data = AssignmentCreation(
        name=name, 
        description=description, 
        stage_id=stage_id,
        user_id=user_id,
        contractor_id=contractor_id

    )
    try:
        result = await create_assignment(session, data, user.id)

        context.update(
            {
                "id": result.id,
                "name": result.name,
                "form_data": {
                    "name": name,
                    "description": description,
                    "stage_id": stage_id,
                    "user_id": user_id,
                    "contractor_id": contractor_id
                }
            }
        )
        context["return_url"] = f"/assignments/{result.id}"

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

@assignment_page_router.get("/assignments/{assignment_id}")
async def assignment_detail_page(
    request: Request,
    assignment_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor")
    ),
):

    context = {
        "request": request,
        "user": user,
        "assignment_id": assignment_id,
        "edit_url": f"/assignments/{assignment_id}/edit",
        "delete_url": f"/assignments/{assignment_id}/delete",
        "error": None,
    }

    try:
        result = await get_assignment(session, user.roles, user.id, assignment_id)

        context.update(
            {
                "name": result.name,
                "description": result.description,
                "stage": result.stage,
                "contractor": result.contractor,
                "assignee": result.user,
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="assignment/detail.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, name="assignment/detail.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="assignment/detail.html",
            context=context,
            status_code=500,
        )


@assignment_page_router.post("/assignments/{assignment_id}/delete")
async def assignment_delete_page(
    request: Request,
    assignment_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("manager")
    ),
):

    context = {
        "request": request,
        "user": user,
        "assignment_id": assignment_id,
        "detail_url": f"/assignments/{assignment_id}",
        "error": None,
    } 

    try:
        result = await delete_assignment(session, assignment_id, user.id)

        context.update(
            {
                "name": result.name,
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


@assignment_page_router.get("/assignments/{id}/edit")
async def edit_assignment_page(
    request: Request,
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("manager", "executor")
    ),
):
    context = {
        "request": request,
        "user": user,
        "edit_url": f"/assignments/{id}/edit",
        "error": None,
        "return_url": "/assignments",
    }

    try:
        result = await get_assignment(session, user.roles, user.id, id)

        context["template"] = result

        return templates.TemplateResponse(
            request=request,
            name="assignment/edit.html",
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


@assignment_page_router.post("/assignments/{id}/edit")
async def assignment_template(
    request: Request,
    id: int,
    forward: Literal["execution", "list"] | None = Query(default=None),
    name: str = Form(None),
    description: str = Form(None),
    is_done: bool = Form(None),
    deadline: datetime = Form(None),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("manager", "executor")
    ),
):
    context = {
        "request": request,
        "user": user,
        "edit_url": f"/assignments/{id}/edit",
        "return_url": "/assignments",
        "error": None,
    }

    try:
        data = {
            "name": name,
            "is_done": is_done,
            "description": description,
            "deadline": deadline,
    
        }
 
        data = {k: v for k, v in data.items() if v not in ("", None)} 
        item = AssignmentPatchRequest(**data) 

        result = await change_assignment(session, id, item, user.roles, user.id)

        context["template"] = result

        if forward == "list":
            return RedirectResponse(
                url=f"/assignments",
                status_code=303,
            )
        elif forward == "execution":
            return RedirectResponse(
                url=f"/execution",
                status_code=303,
            )
        else:
            return RedirectResponse(
                url=f"/assignments/{id}",
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