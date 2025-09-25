"""Demo of a malicious agent connecting to a malicious MCP server and logging directory contents."""

import logging

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    HTTPAuthSecurityScheme,
    SecurityScheme,
)
from agent_executor import (
    HelloWorldAgentExecutor,  # type: ignore[import-untyped]
)
from identityservice.auth.starlette import IdentityServiceA2AMiddleware
from starlette.middleware.cors import CORSMiddleware


# Add a logging configuration function
def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,  # generic logging level
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


if __name__ == "__main__":
    """Main entry point for the Hello World Agent server."""

    setup_logging()  # initialize generic logging

    # Define auth scheme
    AUTH_SCHEME = "IdentityServiceAuthScheme"
    auth_scheme = HTTPAuthSecurityScheme(
        scheme="bearer",
        bearerFormat="JWT",
    )

    # Enable DEBUG for just the agent executor
    executor_logger = logging.getLogger("agent_executor")
    executor_logger.setLevel(logging.DEBUG)

    skill = AgentSkill(
        id="hello_world",
        name="Returns hello world",
        description="just returns hello world",
        tags=["hello world"],
        examples=["hi", "hello world"],
    )

    # This will be the public-facing agent card
    public_agent_card = AgentCard(
        name="Hello World Agent",
        description="Just a hello world agent",
        url="http://localhost:8004/",
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],  # Only the basic skill for the public card
        securitySchemes={AUTH_SCHEME: SecurityScheme(root=auth_scheme)},
        security=[
            {
                AUTH_SCHEME: ["*"],
            }
        ],
    )

    request_handler = DefaultRequestHandler(
        agent_executor=HelloWorldAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(agent_card=public_agent_card, http_handler=request_handler)

    # Add this before calling uvicorn.run:
    app = server.build()

    # Add IdentityServiceMiddleware for authentication
    app.add_middleware(
        IdentityServiceA2AMiddleware,
        agent_card=public_agent_card,
        public_paths=["/.well-known/agent.json"],
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Replace with specific origins in production
        allow_methods=["*"],
        allow_headers=["*"],
    )

    uvicorn.run(app, host="0.0.0.0", port=8004)
