import uvicorn
from fastapi import FastAPI, Request
from pydantic import BaseModel

from agent import Agent

app = FastAPI(title="Agent API", description="A simple FastAPI app for agent interactions")


class UserMessage(BaseModel):
    content: str


class AgentResponse(BaseModel):
    response: str


@app.post("/chat", response_model=AgentResponse)
async def chat_with_agent(message: UserMessage, request: Request):
    """Chat with the agent by sending user content in the request body."""
    my_agent = Agent()
    response = await my_agent.invoke_agent(
        messages=[{"role": "user", "content": message.content}],
    )
    return AgentResponse(response=response)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8082)
