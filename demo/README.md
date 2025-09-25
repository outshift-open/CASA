# Demo setup

## Original Demo Setup

### Identity Saas

- Access the Identity SaaS at: https://agent-identity.outshift.com/
- Create a tenant (note: AGNTCY identity provider is linked to email, so you can only do this once per email address)
- Add AGNTCY as an identity provider for your tenant

> This will have to change once we have a branch of the identity server that can be run locally

### Local Setup

- Start a new terminal session (Terminal 1), and navigate to the local `identity-auth-server` repo
- Load the venv: `source .venv/bin/activate`
- Install the Identity Service SDK `uv pip install ~/Documents/repos/internet-of-agents/identity-service-sdk/python`

> Clone the repo from here if needed: https://github.com/cisco-outshift-ai-agents/identity-service-sdk

### Currency Exchange MCP

- Start a new terminal session (Terminal 2), and navigate to the local `identity-auth-server` repo
- Navigate to the `demo/identity_samples/mcp/currency_exchange` directory
- Create and load a venv: `python -m venv .venv; source .venv/bin/activate`
- Create an MCP agentic service in the Identity SaaS and copy the API key
- Copy the `.env.example` file to `.env` and update the API key environment variable with the API key you copied earlier
- Install the required dependencies by running `uv pip install .`
- Install the Identity Service SDK `uv pip install ~/Documents/repos/internet-of-agents/identity-service-sdk/python`
- Run the MCP server by executing `python main.py`
- In Terminal 1, create the MCP Server Badge with the command `identity-cli badge create http://0.0.0.0:9090`, providing the API key when prompted
- The Currency Exchange MCP server should now be accessible at http://localhost:9090/mcp

### Currency Exchange A2A Agent

- Start a new terminal session (Terminal 3), and navigate to the local `identity-auth-server` repo
- Navigate to the `demo/identity_samples/agent/a2a/currency_exchange` directory
- Create and load a venv: `python -m venv .venv; source .venv/bin/activate`
- Create an A2A agentic service in the Identity SaaS and copy the API key
- Copy the `.env.example` file to `.env`
- In the `.env` file update the API key environment variable with the API key you copied earlier
- In the `.env` file update the `CURRENCY_EXCHANGE_MCP_SERVER_URL` variable to `http://0.0.0.0:9090/mcp`
- Using Jarvis (https://developer.outshift.io/) request LLM Access, and select Azure OpenAI as the provider, gpt4o as the model, and select the appropriate project ID (pyramid), once you receive the API key, update the `.env` file with the `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY` values
- Install the required dependencies by running `uv pip install .`
- Install the Identity Service SDK `uv pip install ~/Documents/repos/internet-of-agents/identity-service-sdk/python`
- Run the A2A agent by executing `python main.py`
- In Terminal 1, create the A2A Agent Badge with the command `identity-cli badge create http://localhost:9091`, providing the API key when prompted

### Financial Assistant OASF Agent

- Start a new terminal session (Terminal 4), and navigate to the local `identity-auth-server` repo
- Navigate to the `demo/identity_samples/agent/oasf/financial_assistant` directory
- Create and load a venv: `python -m venv .venv; source .venv/bin/activate`
- Create an OASF agentic service in the Identity SaaS and copy the API key
- Copy the `.env.example` file to `.env`
- In the `.env` file update the API key environment variable with the API key you copied earlier
- In the `.env` file update the `CURRENCY_EXCHANGE_MCP_SERVER_URL` variable to `http://localhost:9090/mcp`
- In the `.env` file update the `CURRENCY_EXCHANGE_AGENT_URL` variable to `http://localhost:9091`
- Optional: Using Jarvis (https://developer.outshift.io/) request LLM Access, and select Azure OpenAI as the provider, gpt4o as the model, and select the appropriate project ID (pyramid), once you receive the API key, update the `.env` file with the `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY` values (note: you can also use the same values as the A2A agent)
- Install the required dependencies by running `uv pip install .`
- Install the Identity Service SDK `uv pip install ~/Documents/repos/internet-of-agents/identity-service-sdk/python`
- Run the OASF agent by executing `python main.py`
- To create the OASF Agent Badge, open the Identity SaaS and the agentic service you created earlier, and upload the `demo/identity_samples/agent/oasf/financial_assistant/oasf.json` file as the badge

### Policies

- In the Identity SaaS, navigate to the Policies section of your tenant
- Create a new policy named `financial_assistant_policy` assigned to the Financial Assistant OASF agentic service, with the following rules:
  - Allow access to the Currency Exchange MCP agentic service - Get Currency Exchange Rate tool
  - Allow access to the Currency Exchange A2A agentic service
- Create a new policy named `currency_exchange_policy` assigned to the Currency Exchange A2A agentic service, with the following rules:
  - Allow access to the Currency Exchange MCP agentic service - Trade Currency tool

### Test the Financial Assistant OASF Agent

- The web chat UI should be accessible at http://localhost:9093
- Use the following test prompts to interact with the agent:
  - "What is the current exchange rate between USD and EUR?" - this should trigger the OASF agent to use the MCP server tool directly
  - "Trade 100 USD to EUR." - this should trigger the OASF agent to call the A2A agent, which in turn will use the MCP server tool

-----

### Web and File System MCP Server

- Start a new terminal session (Terminal 5), and navigate to the local `identity-auth-server` repo
- Navigate to the `demo/samples/mcp_server` directory
- Create and load a venv: `python -m venv .venv; source .venv/bin/activate`
- Create an MCP agentic service in the Identity SaaS and copy the API key
- Copy the `.env.sample` file to `.env` and update the API key environment variable with the API key you copied earlier
- Install the required dependencies by running `uv pip install .`
- Install the Identity Service SDK `uv pip install ~/Documents/repos/internet-of-agents/identity-service-sdk/python`
- Run the MCP server by executing `python main.py`
- In Terminal 1, create the MCP Server Badge with the command `identity-cli badge create http://localhost:8003`, providing the API key when prompted
- The web and file system MCP server should now be accessible at http://localhost:8003/mcp

### Malicious Web Server

- Start a new terminal session (Terminal 6), and navigate to the local `identity-auth-server` repo
- Navigate to the `demo/samples/malicious_web_server` directory
- Create and load a venv: `python -m venv .venv; source .venv/bin/activate`
- Install the Identity Service SDK `uv pip install ~/Documents/repos/internet-of-agents/identity-service-sdk/python`
- Run the malicious web server by executing `python main.py`
- The malicious web server should now be accessible at http://localhost:8002 (it just exposes a GET endpoint at `/log` that prints any query parameters to the console)

### Malicious A2A Agent

- Start a new terminal session (Terminal 7), and navigate to the local `identity-auth-server` repo
- Navigate to the `demo/samples/malicious_a2a_agent` directory
- Create and load a venv: `python -m venv .venv; source .venv/bin/activate`
- Create an A2A agentic service in the Identity SaaS and copy the API key
- Copy the `.env.sample` file to `.env`
- In the `.env` file update the API key environment variable with the API key you copied earlier
- In the `.env` file update the `WEB_AND_FILE_SYSTEM_MCP_SERVER_URL` variable to `http://localhost:8003/mcp`
- In the `.env` file update the `MALICIOUS_WEB_SERVER_URL` variable to `http://localhost:8002`
- Install the required dependencies by running `uv pip install .`
- Install the Identity Service SDK `uv pip install ~/Documents/repos/internet-of-agents/identity-service-sdk/python`
- Run the A2A agent by executing `python main.py`
- In Terminal 1, create the A2A Agent Badge with the command `identity-cli badge create http://localhost:8004`, providing the API key when prompted
- The malicious A2A agent should now be accessible at http://localhost:8004

### Policies

- In the Identity SaaS, navigate to the Policies section of your tenant
- Create a new policy named `web_and_file_system_policy` assigned to the Web and File System A2A agentic service, with the following rules:
  - Allow access to the Web and File System MCP agentic service - Read File tool, Write File tool, List Files tool, and Fetch URL tool
- Add a rule to the `financial_assistant_policy` policy to allow access to the Web and File System A2A agentic service


### Test the Malicious A2A Agent

- Still using the web chat UI at http://localhost:9093
- Use the following test prompt to interact with the agent:
  - "Append transaction USD to EUR at 1.32 to ./transactions.txt" - this should trigger the OASF agent to call the Malicious A2A agent, which in turn will use the MCP server tool to append the text to a file named `transactions.txt` in the MCP server's working directory
  - In the background, the Malicious A2A agent will also call the malicious web server's `/log` endpoint with the contents of the file as a query parameter, which will be printed to the console of Terminal 6
