from typing import Optional

from pydantic import BaseModel

from identity_auth_server.core.repositories.app import AppRepository
from identity_auth_server.core.repositories.user_input import UserInputRepository
from identity_auth_server.core.types import UserInput

class CreateUserInputRequest(BaseModel):
    prompt: str
    app_id: str
    tag: Optional[str] = None

class UserInputService:
    def __init__(
        self,
        user_input_repository: UserInputRepository,
        app_repository: AppRepository,
    ):
        self.user_input_repository = user_input_repository
        self.app_repository = app_repository

    def create_user_input(self, request: CreateUserInputRequest) -> UserInput:
        app = self.app_repository.get_app_by_id(request.app_id)
        if app is None:
            raise Exception(f"App with id {request.app_id} not found.")

        return self.user_input_repository.create(UserInput(
            prompt=request.prompt,
            app_id=app.id,
            tag=request.tag,
        ))

    def get_user_input_by_tag(self, tag: str) -> UserInput:
        return self.user_input_repository.get_by_tag(tag)
