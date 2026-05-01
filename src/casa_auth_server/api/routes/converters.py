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

"""Converters from domain types to API view models."""

from casa_auth_server.api.routes.view_models import AppViewModel
from casa_auth_server.core.types import App


def to_app_view_model(app: App) -> AppViewModel:
    """Convert an App ORM object to AppViewModel, including the CIMD endpoint URL."""
    vm = AppViewModel.model_validate(app)
    if app.client_credentials:
        vm.client_id_metadata_url = app.client_credentials.client_id
    return vm
