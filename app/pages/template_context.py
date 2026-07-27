from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from app.auth.dependencies import require_page_roles, UserDTO
from app.services.template_context import get_template_vars
from app.config.config import ApplicationException


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

    try:
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