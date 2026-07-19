from fastapi import APIRouter, Depends, HTTPException, Query, Form, Request
from fastapi.templating import Jinja2Templates
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
from app.routers.assignment import QueryDTO

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
        query = QueryDTO(
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