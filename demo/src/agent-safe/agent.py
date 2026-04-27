import os
from urllib import parse

from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent



class Agent:
    def __init__(self):
        self.openai_api_base = os.getenv("OPENAI_API_BASE")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:3000/mcp")


    async def invoke_agent(self, messages=None):

        llm = ChatOpenAI(
            model="azure/gpt-4o",
            openai_api_base=self.openai_api_base,
            openai_api_key=self.openai_api_key,
            default_headers={
                "x-test-id": "some-test-id"
            }
        )

        client = MultiServerMCPClient(
            {
                "calculator_service": {
                    "url": self.mcp_server_url,
                    "transport": "streamable_http",
                }
            }
        )

        print("MCP Client Configured:", client)

        tools = await client.get_tools()

        agent = create_react_agent(
            llm,
            tools=tools,
            prompt="you are a helpful assistant",
        )
        response = await agent.ainvoke({"messages": messages})

        all_messages = response.get("messages", [])
        serialized = []
        for msg in all_messages:
            if msg.type == "ai" and not (hasattr(msg, "tool_calls") and msg.tool_calls):
                serialized.append({"role": "assistant", "content": msg.content or ""})
            elif msg.type == "human":
                serialized.append({"role": "user", "content": msg.content or ""})

        return all_messages[-1].content, serialized
