# pages/common.py

from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.config.config import MANAGEMENT_ROLES
from app.auth.dependencies import UserDTO, require_page_roles
from app.config.config import ApplicationException
from app.config.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.routers.assignment import get_assignments_me, QueryDTO
from app.auth.dependencies import (
    UserDTO,
    get_current_user_from_cookie,
)


common_page_router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)


@common_page_router.get("/")
async def home_page(
    request: Request,
    user: UserDTO = Depends(
        get_current_user_from_cookie
    ),
):

    mode = request.cookies.get(
        "mode",
        "management",
    )

    if mode == "execution":
        return RedirectResponse(
            url="/execution",
            status_code=303,
        )

    return RedirectResponse(
        url="/management",
        status_code=303,
    )


@common_page_router.post("/switch-mode")
async def switch_mode(
    request: Request,
    user: UserDTO = Depends(
        get_current_user_from_cookie
    ),
    mode: str = Form(...),
):
    roles = user.roles

    can_management = bool(MANAGEMENT_ROLES.intersection(set(roles)))

    can_execution = bool("executor" in roles)

    if (mode == "management" and not can_management):
        raise HTTPException(
            status_code=403, detail="Forbidden",
        )

    if (mode == "execution" and not can_execution):
        raise HTTPException(
            status_code=403, detail="Forbidden",
        )

    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="mode", value=mode)

    return response


@common_page_router.get("/execution")
async def execution_page(
    request: Request,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_page_roles("executor")),
    is_done: bool | None = None,
    sort: str | None = None,
    offset: int = 0,
):
    
    query = QueryDTO(
        sort=sort,
        limit=20,
        offset=offset,
        is_done=is_done,
    )
    result = await get_assignments_me(
        session=session,
        query=query,
        user_id=user.id,
    )

    assignments = result.get("items")

    mode = request.cookies.get("mode")
    context = {
        "request": request,
        "user": user,
        "mode": mode,
        "assignments": assignments,
        "total": result.get("total"),
        "limit": result.get("limit"),
        "offset": result.get("offset"),
        "is_done": is_done,
        "sort": sort,
    }
    return templates.TemplateResponse(
        request=request,
        name="common/execution.html",
        context=context,
    )


@common_page_router.get("/management")
async def management_page(
    request: Request,
    user: UserDTO = Depends(
        get_current_user_from_cookie
    ),
):
    return templates.TemplateResponse(
        request=request,
        name="common/management.html",
        context={
            "request": request,
            "user": user,
            "mode": "management",
        },
    )