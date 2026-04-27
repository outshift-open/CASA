# Copyright 2026 Google LLC
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

"""Routing module for User Input operations."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from casa_auth_server.api.dependencies import Container
from casa_auth_server.core.types import UserInput
from casa_auth_server.services.user_input_service import CreateUserInputRequest, UserInputService

router = APIRouter(tags=["UserInputs"])


@router.post("/user-inputs", generate_unique_id_function=lambda _: "create_user_input")
def create_user_input(
    user_input_service: Annotated[UserInputService, Depends(Container.get_user_input_service)],
    request: CreateUserInputRequest,
) -> UserInput:
    """Create a new User Input."""
    user_input = user_input_service.create_user_input(request)
    if user_input.id is None:
        raise HTTPException(status_code=500, detail="User Input creation failed")

    return user_input


@router.get("/user_inputs/get_by_tag/{tag}", generate_unique_id_function=lambda _: "get_user_input_by_tag")
def get_user_input_by_tag(
    user_input_service: Annotated[UserInputService, Depends(Container.get_user_input_service)],
    tag: str,
) -> UserInput:
    """Get a UserInput by tag."""
    user_input = user_input_service.get_user_input_by_tag(tag)
    if not user_input:
        raise HTTPException(status_code=404, detail=f"UserInput with tag '{tag}' not found")

    return user_input
