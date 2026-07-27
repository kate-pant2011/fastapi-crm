from fastapi import APIRouter, Depends, HTTPException, Query, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.config import ApplicationException
from app.config.connection import get_db
from app.auth.dependencies import require_roles
from app.schemas.common import BaseShortResponse, BaseListResponse
from app.services.user import (
    create_user,
    archive_user,
    restore_user,
    get_user_list,
    get_user,
    get_user_me,
    change_user,
    resend_signup_invitation
)
from app.schemas.user import (
    UserItem,
    UserCreationRequest,
    UserCreationResponse,
    UserPatchRequest,
)
from app.auth.dependencies import UserDTO, require_page_roles
from dataclasses import dataclass
from app.routers.user import QueryDTO
from app.services.branch import get_branch_list
from app.routers.branch import BranchQueryDTO


user_page_router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)


@user_page_router.get("/users")
async def user_list_page(
    request: Request,
    branch_id: int | None = Query(default=None),
    role_name: str | None = Query(default=None),
    show_archived: bool = Query(default=False),
    sort: str | None = Query(default=None),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager",)
    ),
):
    context = {
        "request": request,
        "user": user,
        "users": [],
        "branches": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
        "sort": sort,
        "branch_id": branch_id,
        "role_name": role_name,
        "show_archived": show_archived,
        "error": None,
    }
    try:
        query = QueryDTO(
            branch_id=branch_id,
            is_active=False if show_archived else None,
            role_name=role_name,
            sort=sort,
            limit=limit,
            offset=offset,
        )
        result = await get_user_list(session=session, roles=user.roles, query=query)

        branches_result = await get_branch_list(
            session=session,
            query=BranchQueryDTO(limit=1000)
        )

        context.update(
            {
                "users": result.get("items", []),
                "total": result.get("total", 0),
                "limit": result.get("limit", limit),
                "offset": result.get("offset", offset),
                "branches": branches_result.get("items", []),
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="user/list.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, name="user/list.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="user/list.html",
            context=context,
            status_code=500,
        )
    

@user_page_router.get("/profile")
async def user_profile_page(
    request: Request,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor")
    ),
):
    context = {
        "request": request,
        "user": user,
        "error": None,
    }
    try:
        result = await get_user_me(session, user.id)

        context.update(
            {
                "name": result.get("name"),
                "surname": result.get("surname"),
                "position": result.get("position"),
                "email": result.get("email"),
                "clients_count": result.get("clients_count"),
                "assignments_count": result.get("assignments_count"),
                "branch": result.get("branch"),
                "roles": result.get("roles")
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="user/profile.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, name="user/profile.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="user/profile.html",
            context=context,
            status_code=500,
        )
    

@user_page_router.post("/users/{user_id}/delete")
async def user_delete_page(
    request: Request,
    user_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin")
    ),
):

    context = {
        "request": request,
        "user": user,
        "branch_id": user_id, 
        "detail_url": f"/users/{user_id}",
        "return_url":f"/users/{user_id}",
        "error": None,
        "message": None
    }

    try:
        result = await archive_user(session, user_id)

        context.update(
            {
                "name": result.name,
                "message": "удаление"
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="archived_restored.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name
        context["return_url"] = "/users"

        return templates.TemplateResponse(
            request=request, name="error.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"
        context["return_url"] = "/users"

        return templates.TemplateResponse(
            request=request, 
            name="error.html",
            context=context,
            status_code=500,
        )


@user_page_router.post("/users/{user_id}/restore")
async def branch_restore_page(
    request: Request,
    user_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin")
    ),
):

    context = {
        "request": request,
        "user": user,
        "branch_id": user_id, 
        "detail_url": f"/users/{user_id}",
        "return_url":f"/users/{user_id}",
        "error": None,
    }

    try:
        result = await restore_user(session, user_id)

        context.update(
            {
                "name": result.name,
                "message": "восстановление"
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="archived_restored.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name
        context["return_url"] = "/users"

        return templates.TemplateResponse(
            request=request, name="error.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"
        context["return_url"] = "/users"

        return templates.TemplateResponse(
            request=request, 
            name="error.html",
            context=context,
            status_code=500,
        )


@user_page_router.get("/users/{user_id}")
async def user_detail_page(
    request: Request,
    user_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager")
    ),
):

    context = {
        "request": request,
        "user": user,
        "user_id": user_id,
        "error": None,
    }

    try:
        result = await get_user(session, user_id, user.roles)

        context.update(
            {
                "name": result.get("name"),
                "surname": result.get("surname"),
                "position": result.get("position"),
                "email": result.get("email"),
                "clients_count": result.get("clients_count"),
                "assignments_count": result.get("assignments_count"),
                "branch": result.get("branch"),
                "roles": result.get("roles"),
                "is_active": result.get("is_active"),
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="user/detail.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, name="user/detail.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="user/detail.html",
            context=context,
            status_code=500,
        )