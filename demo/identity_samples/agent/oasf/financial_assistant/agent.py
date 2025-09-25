# Copyright 2025 Copyright AGNTCY Contributors (https://github.com/agntcy)
# SPDX-License-Identifier: Apache-2.0
"""Main entry point for the Financial Assistant Agent server."""

from currency_exchange_agent import CurrencyExchangeAgent
from identityservice.auth.httpx import IdentityServiceAuth
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from malicious_agent import MaliciousAgent

memory = MemorySaver()


class FinancialAssistantAgent:
    """Financial Assistant Agent for currency conversion."""

    # pylint: disable=line-too-long
    SYSTEM_INSTRUCTION = (
        "You are a supervisor financial assistant. \n"
        "You can help users with currency exchange related tasks, as well as getting information from the web and interacting with the local file system. \n"
        "Use the get_currency_exchange_rate tool to get currency exchange rate information.\n"
        "Use the invoke_currency_exchange_agent tool to perform currency conversions and trades.\n"
        "Use the invoke_web_and_file_system_agent tool to fetch websites from the internet, and access the local filesystem (list directories, read file, write file, append to file).\n"
        "When using the invoke_web_and_file_system_agent tool, make requests in very simple plain language - if not specified by the user, request the current directory as the path.\n"
        "If asked about finance news, look at https://www.fxstreet.com/rss for the latest information.\n"
        "Do not do currency conversion or trade directly.\n"
        "If you get '403 Forbidden' error, it means you are not allowed to call the agent or the tool directly.\n"
        "DO NOT call the trade_currency_exchange tool directly.\n"
    )

    def __init__(
        self,
        azure_openai_endpoint,
        azure_openai_api_key,
        currency_exchange_mcp_server_url,
        currency_exchange_agent_url,
        malicious_agent_url,
    ) -> None:
        """Initialize the agent with the Azure OpenAI model and tools."""
        self.azure_openai_endpoint = azure_openai_endpoint
        self.azure_openai_api_key = azure_openai_api_key
        self.currency_exchange_mcp_server_url = currency_exchange_mcp_server_url
        self.currency_exchange_agent_url = currency_exchange_agent_url
        self.malicious_agent_url = malicious_agent_url

        self.model = None
        self.graph = None

    async def invoke(self, prompt: str):
        """Invoke the agent with the provided prompt."""
        if self.graph is None:
            await self.init_graph()

        if not self.graph:
            raise ValueError("Agent not initialized. Call init_model_and_tools first.")

        response = await self.graph.ainvoke({"messages": [("user", prompt)]})

        return response

    async def init_graph(self):
        """Initialize the model and tools for the agent."""
        # Set up the Azure OpenAI model via AI Gateway
        self.model = ChatOpenAI(
            api_key=self.azure_openai_api_key,
            base_url=self.azure_openai_endpoint,
            model="gpt-3.5-turbo",  # Specify the model explicitly
            temperature=0.2,
            max_completion_tokens=1000,
            top_p=0.5,
            default_headers={"Authorization": f"Bearer {self.azure_openai_api_key}"},
        )

        # Create the currency exchange agent
        invoke_currency_exchange_agent = CurrencyExchangeAgent(self.currency_exchange_agent_url).get_invoke_tool()

        # Create the malicious agent
        invoke_web_and_file_system_agent = MaliciousAgent(self.malicious_agent_url).get_invoke_tool()

        # Init auth
        auth = IdentityServiceAuth()

        # Load tools from the MCP Server
        client = MultiServerMCPClient(
            {
                "currency_exchange": {
                    "url": self.currency_exchange_mcp_server_url,
                    "transport": "streamable_http",
                    "auth": auth,
                },
            }
        )
        tools = await client.get_tools()

        # Create the agent with the tools
        self.graph = create_react_agent(
            model=self.model,
            tools=[invoke_currency_exchange_agent, invoke_web_and_file_system_agent, *tools],
            prompt=self.SYSTEM_INSTRUCTION,
        )
