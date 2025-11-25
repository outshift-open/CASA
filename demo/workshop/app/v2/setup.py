from setuptools import find_packages, setup

setup(
    name="agentapp",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "langchain-litellm",
        "langgraph",
        "langchain-mcp-adapters",
        "identity-auth-server",
    ],
)
