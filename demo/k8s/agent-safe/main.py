import uvicorn
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
    uvicorn.run(app, host="0.0.0.0", port=8082)
