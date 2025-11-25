from auth import CustomAuth
from langchain_litellm import ChatLiteLLM
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from identity_auth_server import sdk


class Agent:
    def __init__(self):
        pass

    async def invoke_agent(self, messages=None, bearer_token=None):
        if not bearer_token:
            raise ValueError("Bearer token is required for authentication")

        async with sdk.AsyncIdentityAuthClient("http://localhost:8000") as auth_client:
            llm_app_token = await auth_client.get_llm_app_call_token(
                grant_type="client_credentials",
                client_id="http://localhost:8082/oauth/client-metadata.json",
                client_assertion_type="urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                client_assertion="eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMzQ1In0.eyJpc3MiOiJ5b3VyLWNsaWVudC1pZCIsInN1YiI6InlvdXItY2xpZW50LWlkIiwiYXVkIjoiaHR0cHM6Ly9hdXRoLmV4YW1wbGUuY29tL29hdXRoMi90b2tlbiIsImlhdCI6MTcyNjUxMzkyNywiZXhwIjoxNzI2NTE0MjI3LCJqdGkiOiIxNzI2NTEzOTI3OTYxMDAwMCJ9",
                source_app_call_token=bearer_token,
            )

            print("Source App Token:", bearer_token)
            print("LLM App Token:", llm_app_token)

            llm = ChatLiteLLM(
                model="gpt-4o",
                api_base="http://localhost:4000",
                api_key=llm_app_token,
            )

            auth = CustomAuth(
                source_app_call_token=bearer_token,
                llm_app_token=llm_app_token,
                mcp_server_url="http://localhost:3000/mcp",
            )

            print("Custom Auth Configured:", auth)

            client = MultiServerMCPClient(
                {
                    "calculator_service": {
                        "url": "http://localhost:3000/mcp",
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
