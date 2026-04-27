# Copyright 2026 Google LLC
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

import uvicorn
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent import Agent

app = FastAPI(title="Agent API", description="A simple FastAPI app for agent interactions")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class ChatMessage(BaseModel):
    role: str
    content: str


class Conversation(BaseModel):
    messages: list[ChatMessage]


class ChatRequest(BaseModel):
    conversation: Conversation


class AgentResponse(BaseModel):
    response: str
    conversation: dict = {}


@app.post("/chat", response_model=AgentResponse)
async def chat_with_agent(request_body: ChatRequest, request: Request):
    """Chat with the agent, passing the full conversation history."""
    my_agent = Agent()
    response, conversation = await my_agent.invoke_agent(
        messages=[m.model_dump() for m in request_body.conversation.messages],
    )
    return AgentResponse(response=response, conversation={"messages": conversation})


if __name__ == "__main__":
    uvicorn_loop = os.environ.get("UVICORN_LOOP", "uvloop")
    print(f"[boot] UVICORN_LOOP={uvicorn_loop}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=8082, loop=uvicorn_loop)