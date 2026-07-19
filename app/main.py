from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
import app.models_loader
import logging
from logging.handlers import RotatingFileHandler
from .middleware.auth import RefreshMiddleware
from .middleware.logging import log_requests
from .auth.router import auth_router
from .auth.pages import auth_page_router
from .email.router import email_router
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
from .routers.file import file_router
from .routers.email_log import email_log_router
from .routers.email_template import email_template_router
from .routers.template import template_router
from .routers.doc_template import doc_template_router
from .routers.generated_doc import generated_doc_router
from .pages.common import common_page_router
from .pages.user import user_page_router
from .pages.assignment import assignment_page_router
from .pages.client import client_page_router
from .pages.company import company_page_router
from .pages.contract import contract_page_router
from .pages.project import project_page_router
from .pages.stage_template import stage_template_page_router
from .pages.email_template import email_template_page_router
from .pages.doc_template import doc_template_page_router
from .pages.generated_doc import generated_doc_page_router
from .pages.branch import branch_page_router
from .pages.contractor import contractor_page_router
from .pages.template_context import template_fields_page_router
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.rate_limit import limiter


app = FastAPI()

templates = Jinja2Templates(
    directory="app/templates"
)
app.add_middleware(RefreshMiddleware)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.middleware("http")(log_requests)

app.include_router(auth_router)
app.include_router(email_router)
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
app.include_router(file_router)
app.include_router(email_log_router)
app.include_router(email_template_router)
app.include_router(doc_template_router)
app.include_router(template_router)
app.include_router(generated_doc_router)

app.include_router(auth_page_router)
app.include_router(common_page_router)
app.include_router(user_page_router)
app.include_router(assignment_page_router)
app.include_router(client_page_router)
app.include_router(company_page_router)
app.include_router(contract_page_router)
app.include_router(project_page_router)
app.include_router(stage_template_page_router)
app.include_router(email_template_page_router)
app.include_router(doc_template_page_router)
app.include_router(generated_doc_page_router)
app.include_router(branch_page_router)
app.include_router(contractor_page_router)
app.include_router(template_fields_page_router)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

handler = RotatingFileHandler(
    "app.log",
    maxBytes=1_000_000,
    backupCount=3
)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)


