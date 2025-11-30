from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware


import os, sys


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))


from gigachat_api.endpoints.oauth import app as token_router
from gigachat_api.endpoints.models import app as model_router
from gigachat_api.endpoints.chat import app as chat_router
from utils.logger import logger



@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("[SERIVCE]: starting lifespan")
    yield
    logger.info("[SERVICE]: shutting down lifespan")


app = FastAPI(
    title="HH Resume parsing",
    description="API service for gigachat api",
    version="1.0.0",
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(token_router, prefix="/token", tags=["Authentication"])
app.include_router(model_router, prefix="/models", tags=["All accessable gigachat models"])
app.include_router(chat_router, prefix="/chat", tags=["Chat actions"])

logger.info("[SERIVCE]: initialized")