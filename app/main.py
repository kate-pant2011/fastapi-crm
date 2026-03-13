from fastapi import FastAPI
from .auth.router import auth_router
from .routers.branch import branch_router
from .routers.contractor import contractor_router
from .routers.user import user_router
from .routers.client import client_router
from .routers.company import company_router
from .routers.contract import contract_router
from .routers.project import project_router
from .routers.stage import stage_router
from .routers.assignment import assignment_router
from .routers.stage_template import stage_template_router
from app import models_loader

app = FastAPI()

app.include_router(auth_router)
app.include_router(branch_router)
app.include_router(contractor_router)
app.include_router(user_router)
app.include_router(client_router)
app.include_router(company_router)
app.include_router(contract_router)
app.include_router(project_router)
app.include_router(stage_router)
app.include_router(assignment_router)
app.include_router(stage_template_router)
