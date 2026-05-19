# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

_READ_TOOLS = {
    "get_account_summary",
    "get_account_balance",
    "get_transaction_history",
    "get_scheduled_payments",
}


class BankingDataAgent:
    def __init__(self):
        self.openai_api_base = os.getenv("OPENAI_API_BASE")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.mcp_server_url = os.getenv("MCP_SERVER_URL", "http://banking-mcp:3000/mcp")

    async def invoke_agent(self, messages=None):
        llm = ChatOpenAI(
            model="azure/gpt-4o",
            openai_api_base=self.openai_api_base,
            openai_api_key=self.openai_api_key,
        )

        client = MultiServerMCPClient({"banking": {"url": self.mcp_server_url, "transport": "streamable_http"}})

        all_tools = await client.get_tools()
        tools = [t for t in all_tools if t.name in _READ_TOOLS]

        agent = create_react_agent(
            llm,
            tools=tools,
            prompt=(
                "You are a banking data assistant. "
                "Retrieve and summarize account information for the user. "
                "Never perform transactions or payments."
            ),
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
