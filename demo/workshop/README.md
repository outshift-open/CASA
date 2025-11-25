python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Add the master key - you can change this after setup

echo 'LITELLM_MASTER_KEY="sk-1234"' > .env

# password generator to get a random hash for litellm salt key

echo 'LITELLM_SALT_KEY="sk-1234"' >> .env

source .env

cd /Users/beryder/Documents/repos/ZTA/identity-auth-server/src/identity_auth_server

uv pip install /Users/beryder/Documents/repos/ZTA/identity-auth-server

---

LiteLLM

`cd llm`
`litellm --config config.yaml`

Agent

`cd app`
`python main.py`

MCP Server

`cd mcp`
`uvicorn main:app --reload --host`
