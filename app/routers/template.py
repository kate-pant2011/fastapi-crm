from fastapi import APIRouter, Depends
from app.auth.dependencies import require_roles
from app.auth.dependencies import UserDTO
from app.services.template_context import get_template_vars
from pydantic import BaseModel

template_router = APIRouter()

class TemplateVars(BaseModel):
    variables: list[str]

@template_router.get("/template/variables", response_model=TemplateVars)
async def get_template_vars_router(
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    return get_template_vars()