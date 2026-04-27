import logging
from typing import Optional

from pydantic import BaseModel

from casa_auth_server.core.repositories.app import AppRepository
from casa_auth_server.core.repositories.user_input import UserInputRepository
from casa_auth_server.core.types import UserInput
from casa_auth_server.pipelines.conversation.tbac_components import TaskExtractor

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class CreateUserInputRequest(BaseModel):
    prompt: str
    app_id: str
    tag: Optional[str] = None


class UserInputService:
    def __init__(
        self,
        user_input_repository: UserInputRepository,
        app_repository: AppRepository,
        task_extractor: TaskExtractor,
    ):
        self.user_input_repository = user_input_repository
        self.app_repository = app_repository
        self.task_extractor = task_extractor

    def create_user_input(self, request: CreateUserInputRequest) -> UserInput:
        app = self.app_repository.get_app_by_id(request.app_id)
        if app is None:
            raise Exception(f"App with id {request.app_id} not found.")

        try:
            task = self.task_extractor.extract_task(request.prompt)
            if task is None:
                logger.error("task is none, fallbacking to the whole conversation")
        except Exception as e:
            logger.error(
                f"failed to extract the task from the conversation, fallbacking to the whole conversation: {e}"
            )

        if task is None:
            task = request.prompt

        return self.user_input_repository.create(
            UserInput(
                prompt=task,
                app_id=app.id,
                tag=request.tag,
            )
        )

    def get_user_input_by_tag(self, tag: str) -> UserInput:
        return self.user_input_repository.get_by_tag(tag)
