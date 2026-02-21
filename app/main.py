from fastapi import FastAPI
from .auth.router import auth_router
from .routers.branch import branch_router
from .routers.contractor import contractor_router
from .routers.user import user_router
from .config.connection import engine

app = FastAPI()

app.include_router(auth_router)
app.include_router(branch_router)
app.include_router(contractor_router)
app.include_router(user_router)