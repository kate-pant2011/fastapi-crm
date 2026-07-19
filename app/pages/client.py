from fastapi import APIRouter, Depends, HTTPException, Query, Form, Request
from fastapi.templating import Jinja2Templates
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import require_page_roles
from app.auth.dependencies import UserDTO
from app.config.connection import get_db
from app.schemas.common import BaseShortResponse, BaseListResponse
from app.schemas.client import ClientItem, ClientCreation, ClientPatchRequest
from app.services.client import (
    form_client_list,
    get_client,
    create_client,
    archive_client,
    restore_client,
    change_client,
)
from app.routers.client import ClientQueryDTO
from app.routers.user import get_user_list, QueryDTO
from typing import Literal

client_page_router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)


@client_page_router.get("/clients")
async def client_list_page(
    request: Request,
    scope: Literal["mine"] | None = Query(
        default=None, description="scope ignored if manager_id provided"
    ),
    manager_id: int | None = Query(default=None),
    sort: str | None = Query(default=None),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager"))
):
    context = {
        "request": request,
        "user": user,
        "clients": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
        "sort": sort,
        "manager_id": manager_id,
        "scope": scope,
        "error": None,
    }
    try:
        query = ClientQueryDTO(
            sort=sort,
            limit=limit,
            offset=offset,
            manager_id=manager_id,
            scope=scope
        )
        result = await form_client_list(
            session=session, roles=user.roles, requester_id=user.id, query=query
        )

        managers_result = await get_user_list(
            session=session, roles=user.roles, query=QueryDTO(
                role_name="manager", limit=1000
            )
        )

        context.update(
            {
                "clients": result.get("items", []),
                "total": result.get("total", 0),
                "limit": result.get("limit", limit),
                "offset": result.get("offset", offset),
                "managers": managers_result.get("items", [])
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="client/list.html",
            context=context,
        )

    except ApplicationException as e:
        context["error"] = e.name

        return templates.TemplateResponse(
            request=request, 
            name="client/list.html", 
            context=context,
            status_code=e.code,
        )

    except Exception as e:
        context["error"] = f"{type(e).__name__} - {e}"

        return templates.TemplateResponse(
            request=request, 
            name="client/list.html",
            context=context,
            status_code=500,
        )