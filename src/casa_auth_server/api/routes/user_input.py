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
