import os
from urllib import parse
from auth import CustomAuth
from langchain_litellm import ChatLiteLLM
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

import identity_auth_sdk


class Agent:
    def __init__(self):
        self.auth_server_url = os.getenv("AUTH_SERVER_URL", "http://localhost:8000")
        self.litellm_url = os.getenv("LITELLM_URL", "http://localhost:4000")
        self.mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:3000/mcp")
        self.agent_app_id = os.getenv("AGENT_APP_ID", "")
        self.agent_client_id = os.getenv("AGENT_CLIENT_ID", "")
        self.agent_client_secret = os.getenv("AGENT_SECRET", "")
        self.sdk_config = identity_auth_sdk.Configuration(
            host = self.auth_server_url
        )

    async def invoke_agent(self, messages=None, bearer_token=None):
        if not bearer_token:
            raise ValueError("Bearer token is required for authentication")

        with identity_auth_sdk.ApiClient(self.sdk_config) as api_client:
            api_instance = identity_auth_sdk.DefaultApi(api_client)

            llm_app_token = api_instance.token_exchange(
                app_id=self.agent_app_id,
                client_id=self.agent_client_id,
                client_secret=self.agent_client_secret,
                subject_token=bearer_token,
                subject_token_type="urn:ietf:params:oauth:token-type:access_token",
            )
            llm_app_token = llm_app_token.access_token

            print("Source App Token:", bearer_token)
            print("LLM App Token:", llm_app_token)

            llm = ChatLiteLLM(
                model="gpt-4o",
                api_base=self.litellm_url,
                api_key=llm_app_token,
            )

            auth = CustomAuth(
                source_app_call_token=bearer_token,
                llm_app_token=llm_app_token,
                mcp_server_url=self.mcp_server_url,
            )

            print("Custom Auth Configured:", auth)

            client = MultiServerMCPClient(
                {
                    "calculator_service": {
                        "url": self.mcp_server_url,
                        "transport": "streamable_http",
                        "auth": auth,
                    }
                }
            )

            print("MCP Client Configured:", client)

            tools = await client.get_tools()
            agent = create_react_agent(llm, tools=tools, prompt="you are a helpful assistant")
            response = await agent.ainvoke({"messages": messages})
            return response.get("messages")[-1].content
