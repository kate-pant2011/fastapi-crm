from fastapi import FastAPI
import uvicorn
from .auth.router import auth_router
from .database.connection import engine



app = FastAPI()

app.include_router(auth_router)

