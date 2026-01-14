import os
from typing import Any, Dict, Optional

from litellm.integrations.custom_logger import CustomLogger
from litellm.types.utils import ModelResponse

import identity_auth_sdk


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
        print(f"------ log_pre_api_call ------\n")

        sdk_config = identity_auth_sdk.Configuration(
            host = os.getenv("AUTH_SERVER_URL", "http://localhost:8000"),
            access_token = self._extract_user_api_key(kwargs)
        )

        with identity_auth_sdk.ApiClient(sdk_config) as api_client:
            api_instance = identity_auth_sdk.DefaultApi(api_client)
            _ = api_instance.trace_llm_call_start(
                identity_auth_sdk.LLMCallStartedRequest(
                    call_id=kwargs.get("litellm_call_id", ""),
                    prompt=str(messages),
                    tools=str(kwargs.get("optional_params", {}).get("tools", [])),
                )
            )

        # self._log_event("On Pre-API Call", messages=messages, kwargs=kwargs, log_messages=True, log_tools=True)

    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        print(f"------ log_pre_api_call ------\n")

        sdk_config = identity_auth_sdk.Configuration(
            host = os.getenv("AUTH_SERVER_URL", "http://localhost:8000"),
            access_token = self._extract_user_api_key(kwargs)
        )

        with identity_auth_sdk.ApiClient(sdk_config) as api_client:
            api_instance = identity_auth_sdk.DefaultApi(api_client)
            _ = api_instance.trace_llm_call_end(
                identity_auth_sdk.LLMCallEndedRequest(
                    call_id=kwargs.get("litellm_call_id", ""),
                    response=str(
                        response_obj.choices[0].message.content
                        if response_obj.choices and len(response_obj.choices) > 0
                        else ""
                    ),
                    tools=str(
                        response_obj.choices[0].message.tool_calls
                        if response_obj.choices and len(response_obj.choices) > 0
                        else None
                    ),
                )
            )

        # self._log_event("On LLM Success", response_obj=response_obj, kwargs=kwargs, log_response=True)

    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        print(f"------ async_log_success_event ------\n")

        sdk_config = identity_auth_sdk.Configuration(
            host = os.getenv("AUTH_SERVER_URL", "http://localhost:8000"),
            access_token = self._extract_user_api_key(kwargs)
        )

        with identity_auth_sdk.ApiClient(sdk_config) as api_client:
            api_instance = identity_auth_sdk.DefaultApi(api_client)
            _ = api_instance.trace_llm_call_end(
                identity_auth_sdk.LLMCallEndedRequest(
                    call_id=kwargs.get("litellm_call_id", ""),
                    response=str(
                        response_obj.choices[0].message.content
                        if response_obj.choices and len(response_obj.choices) > 0
                        else ""
                    ),
                    tools=str(
                        response_obj.choices[0].message.tool_calls
                        if response_obj.choices and len(response_obj.choices) > 0
                        else None
                    ),
                )
            )

        # self._log_event("On Async LLM Success", response_obj=response_obj, kwargs=kwargs, log_response=True)
        return


proxy_handler_instance = MyCustomHandler()
