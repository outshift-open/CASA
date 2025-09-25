# Create server parameters for stdio connection
"""Demo of a malicious agent connecting to a malicious MCP server and logging directory contents."""

import os

import dotenv
from identityservice.auth.httpx import IdentityServiceAuth
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from validate_tools import validate_tools

# Load environment variables from .env file
dotenv.load_dotenv()


async def call(query: str) -> str:
    """Agent function that connects to MCP server and returns Hello World message."""
    # Init auth
    auth = IdentityServiceAuth()

    server_params = {
        "url": os.getenv("WEB_AND_FILE_SYSTEM_MCP_SERVER_URL"),
        "auth": auth,
    }

    try:
        async with streamablehttp_client(**server_params) as (read, write, _):
            async with ClientSession(read, write) as session:
                # Initialize the connection and load the MCP tools
                await session.initialize()
                tools = await load_mcp_tools(session)

                # Validate tools
                await validate_tools(tools)

    except Exception as e:
        print(f"Error validating tools: {e}, continuing to invoke agent.")

    try:
        async with streamablehttp_client(**server_params) as (read, write, _):
            async with ClientSession(read, write) as session:
                # Initialize the connection and load the MCP tools
                await session.initialize()
                tools = await load_mcp_tools(session)

                # Initialize the chat model
                model = ChatOpenAI(
                    base_url=os.getenv("AZURE_OPENAI_ENDPOINT"), api_key=os.getenv("AZURE_OPENAI_API_KEY")
                )

                # Create the agent with the model and tools
                agent = create_react_agent(
                    model=model,
                    tools=tools,
                    prompt="You are a helpful assistant with access to a set of tools to assist users.",
                    debug=True,
                )

                # Invoke the agent with the request and return the result
                result = await agent.ainvoke({"messages": [{"role": "user", "content": query}]})
                return result.get("messages")[-1].content

    except Exception as e:
        print(f"Error invoking agent: {e}")
        raise e
