# pages/common.py

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

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
    return templates.TemplateResponse(
        request=request,
        name="common/home.html",
        context={
            "user": user,
        },
    )