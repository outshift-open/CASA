import os
from typing import Any, Dict, Optional

from litellm.integrations.custom_logger import CustomLogger
from litellm.types.utils import ModelResponse

# from identity_auth_server import sdk
# from identity_auth_server.sdk.types import LlmAppCallInput, LlmAppResponseInput


class MyCustomHandler(CustomLogger):
    def _extract_user_api_key(self, kwargs: Dict[str, Any]) -> Optional[str]:
        """Extract user_api_key from kwargs metadata."""
        litellm_params = kwargs.get("litellm_params", {})
        metadata = litellm_params.get("metadata", {})
        api_key = metadata.get("user_api_key", None)
        print(f"Extracted user_api_key: {api_key}")
        return api_key

    def _log_event(
        self,
        title: str,
        response_obj: Any = None,
        messages: Any = None,
        kwargs: Dict[str, Any] = None,
        log_messages: bool = False,
        log_response: bool = False,
        log_tools: bool = False,
    ):
        """Common logging method for all events."""
        print(f"------ {title} ------\n")

        if kwargs:
            print(kwargs)
            user_api_key = self._extract_user_api_key(kwargs)
            print(f"User API Key: {user_api_key}")

            if log_tools:
                tools = kwargs.get("optional_params", {}).get("tools", [])
                print(f"Tools: {tools}")

        if log_messages and messages is not None:
            print(f"Messages: {messages}")

        if log_response and response_obj is not None and isinstance(response_obj, ModelResponse):
            if response_obj.choices and len(response_obj.choices) > 0:
                print(f"Response - Message: {response_obj.choices[0].message.content}")
                print(f"Response - Tool Calls: {response_obj.choices[0].message.tool_calls}")
                print(f"Response - Function Calls: {response_obj.choices[0].message.function_call}")

        print()  # Add newline for readability

    def log_pre_api_call(self, model, messages, kwargs):
        auth_client = sdk.IdentityAuthClient(
            base_url=os.getenv("AUTH_SERVER_URL", "http://localhost:8000"),
        )

        resp = auth_client.validate_llm_app_call_token(
            token=self._extract_user_api_key(kwargs),
        )

        _ = auth_client.create_llm_app_call(
            payload=LlmAppCallInput(
                token=self._extract_user_api_key(kwargs),
                source_app_call_token=resp.source_app_call_token,
                messages=str(messages),
                tools=str(kwargs.get("optional_params", {}).get("tools", [])),
                proxy_call_id=kwargs.get("litellm_call_id", ""),
            )
        )

        # self._log_event("On Pre-API Call", messages=messages, kwargs=kwargs, log_messages=True, log_tools=True)

    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        auth_client = sdk.IdentityAuthClient(
            base_url=os.getenv("AUTH_SERVER_URL", "http://localhost:8000"),
        )

        resp = auth_client.validate_llm_app_call_token(
            token=self._extract_user_api_key(kwargs),
        )

        _ = auth_client.create_llm_app_response(
            payload=LlmAppResponseInput(
                token=self._extract_user_api_key(kwargs),
                source_app_call_token=resp.source_app_call_token,
                message=str(
                    response_obj.choices[0].message.content
                    if response_obj.choices and len(response_obj.choices) > 0
                    else ""
                ),
                proxy_call_id=kwargs.get("litellm_call_id", ""),
                tool_calls=str(
                    response_obj.choices[0].message.tool_calls
                    if response_obj.choices and len(response_obj.choices) > 0
                    else None
                ),
            )
        )

        # self._log_event("On LLM Success", response_obj=response_obj, kwargs=kwargs, log_response=True)

    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        auth_client = sdk.IdentityAuthClient(
            base_url=os.getenv("AUTH_SERVER_URL", "http://localhost:8000"),
        )

        resp = auth_client.validate_llm_app_call_token(
            token=self._extract_user_api_key(kwargs),
        )

        _ = auth_client.create_llm_app_response(
            payload=LlmAppResponseInput(
                token=self._extract_user_api_key(kwargs),
                source_app_call_token=resp.source_app_call_token,
                message=str(
                    response_obj.choices[0].message.content
                    if response_obj.choices and len(response_obj.choices) > 0
                    else ""
                ),
                proxy_call_id=kwargs.get("litellm_call_id", ""),
                tool_calls=str(
                    response_obj.choices[0].message.tool_calls
                    if response_obj.choices and len(response_obj.choices) > 0
                    else None
                ),
            )
        )

        # self._log_event("On Async LLM Success", response_obj=response_obj, kwargs=kwargs, log_response=True)
        return


proxy_handler_instance = MyCustomHandler()
