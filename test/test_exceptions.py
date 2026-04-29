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

"""Unit tests for domain exception types."""

import pytest

from casa_auth_server.core.exceptions import ResourceAlreadyExistsError, ResourceNotFoundError
from casa_auth_server.pipelines.exceptions import PipelineValidationError


def test_resource_not_found_error_is_exception() -> None:
    with pytest.raises(ResourceNotFoundError) as exc_info:
        raise ResourceNotFoundError("entity-123")
    assert isinstance(exc_info.value, Exception)


def test_resource_already_exists_error_is_exception() -> None:
    with pytest.raises(ResourceAlreadyExistsError) as exc_info:
        raise ResourceAlreadyExistsError("entity-456")
    assert isinstance(exc_info.value, Exception)


def test_pipeline_validation_error_stores_message() -> None:
    err = PipelineValidationError("bad input")
    assert err.message == "bad input"
    assert str(err) == "bad input"
