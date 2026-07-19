from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from app.auth.dependencies import require_page_roles, UserDTO
from app.services.template_context import get_template_vars


template_fields_page_router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)

@template_fields_page_router.get("/template-fields")
async def template_fields_list_page(
    request: Request,
    user: UserDTO = Depends(
        require_page_roles("owner", "admin", "manager", "executor"))
):
    result = get_template_vars()

    context = {
        "template_fields": result,
        "request": request,
        "user": user,
    }

    return templates.TemplateResponse(
        request=request,
        name="template_fields.html",
        context=context,
    )