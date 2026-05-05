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

"""Metrics service — aggregated statistics for the Explorer UI dashboard."""

from casa_auth_server.core.repositories.multi_agent_system import MultiAgentSystemRepository
from casa_auth_server.telemetry.tracer_repository import MetricsSnapshot, TracerRepository


class MetricsService:
    """Computes pre-aggregated metrics."""

    def __init__(self, tracer_repository: TracerRepository, mas_repository: MultiAgentSystemRepository):
        """Initialize with backing repositories."""
        self._tracer_repository = tracer_repository
        self._mas_repository = mas_repository

    def get_metrics(self) -> MetricsSnapshot:
        """Return a metrics snapshot in a single call."""
        total_mas = len(self._mas_repository.get_all())
        return self._tracer_repository.get_metrics(total_mas)
