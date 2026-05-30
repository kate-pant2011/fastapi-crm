from fastapi import FastAPI
import app.models_loader
import logging
from logging.handlers import RotatingFileHandler
from .middleware import log_requests
from .auth.router import auth_router
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


app = FastAPI()

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


