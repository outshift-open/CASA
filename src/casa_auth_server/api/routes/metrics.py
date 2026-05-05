# Copyright 2026 Cisco Systems, Inc. and its affiliates
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

"""Metrics endpoint — pre-aggregated statistics for the Explorer UI dashboard."""

from typing import Annotated

from fastapi import APIRouter, Depends

from casa_auth_server.api.dependencies import Container
from casa_auth_server.services.metrics_service import MetricsService
from casa_auth_server.telemetry.tracer_repository import MetricsSnapshot

router = APIRouter(tags=["Metrics"])


@router.get("/metrics")
def get_metrics(
    metrics_service: Annotated[MetricsService, Depends(Container.get_metrics_service)],
) -> MetricsSnapshot:
    """Return a pre-aggregated metrics snapshot."""
    return metrics_service.get_metrics()
