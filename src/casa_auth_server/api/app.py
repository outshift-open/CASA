# Copyright 2025 Cisco Systems, Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""API for Identity Service CASA."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from casa_auth_server.api.dependencies import Container
from casa_auth_server.api.routes import app as app_routes
from casa_auth_server.api.routes import authorization as authorization_routes
from casa_auth_server.api.routes import k8s as k8s_routes
from casa_auth_server.api.routes import k8s_crd as k8s_crd_routes
from casa_auth_server.api.routes import multi_agent_system as mas_routes
from casa_auth_server.api.routes import scope as scope_routes
from casa_auth_server.api.routes import trace as trace_routes
from casa_auth_server.api.routes import user_input as user_input_routes

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
app.include_router(scope_routes.router)
app.include_router(k8s_crd_routes.router)
app.include_router(user_input_routes.router)
app.include_router(k8s_routes.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
