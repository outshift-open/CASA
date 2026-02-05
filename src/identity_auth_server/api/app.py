"""API for Identity Service ZTA."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from identity_auth_server.api.dependencies import Container
from identity_auth_server.api.routes import app as app_routes
from identity_auth_server.api.routes import authorization as authorization_routes
from identity_auth_server.api.routes import multi_agent_system as mas_routes
from identity_auth_server.api.routes import trace as trace_routes

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s  [%(name)s] %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Application lifespan manager that runs migrations on startup."""
    logger.info("Application starting up...")
    yield


app = FastAPI(lifespan=lifespan)

Container()

app.include_router(authorization_routes.router)
app.include_router(app_routes.router)
app.include_router(trace_routes.router)
app.include_router(mas_routes.router)

# Allow all origins (for local development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
