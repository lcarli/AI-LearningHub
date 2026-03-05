---
tags: [foundry, mcp, azure, azure-required, persona-developer, persona-architect]
---
# Lab 030: Microsoft Foundry Agent Service + MCP

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Path:</strong> <a href="../paths/foundry/">Foundry + MCP</a></span>
  <span><strong>Time:</strong> ~90 min</span>
  <span><strong>💰 Cost:</strong> Azure subscription — gpt-4o-mini token costs</span>
</div>

!!! warning "Azure subscription required"
    This lab requires an Azure subscription. → [Prerequisites guide](../prerequisites.md)

## What You'll Learn

- Deploy **Azure AI Foundry** Hub + Project with one click
- Deploy a **gpt-4o-mini** model endpoint
- Create an **Agent** in the Foundry Agent Service
- Connect your MCP server as a tool for the agent
- Run an end-to-end agent conversation with tool calls

---

## Deploy Infrastructure

### Option A — Deploy to Azure (one click)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Flcarli%2FAI-LearningHub%2Fmain%2Finfra%2Flab-030-foundry%2Fazuredeploy.json)

This deploys:
- Azure AI Foundry Hub
- AI Project (OutdoorGear Agent Project)
- Storage Account + Key Vault (required by Foundry)

!!! tip "Recommended location"
    Use **East US** or **Sweden Central** for best model availability.

### Option B — Azure CLI (Bicep)

```bash
git clone https://github.com/lcarli/AI-LearningHub.git && cd AI-LearningHub

az group create --name rg-ai-labs-foundry --location eastus

# Get your user Object ID
USER_OID=$(az ad signed-in-user show --query id -o tsv)

az deployment group create \
  --resource-group rg-ai-labs-foundry \
  --template-file infra/lab-030-foundry/main.bicep \
  --parameters location=eastus userObjectId=$USER_OID
```

---

## Lab Exercise

### Step 1: Deploy gpt-4o-mini in Foundry

1. Go to [ai.azure.com](https://ai.azure.com) → your project
2. **Model catalog** → search `gpt-4o-mini` → **Deploy**
3. Name: `gpt-4o-mini` — keep defaults
4. Copy your **endpoint URL** and **API key** from the deployment page

### Step 2: Start your MCP server

Use the server from [Lab 020](lab-020-mcp-server-python.md) or [Lab 028](lab-028-deploy-mcp-azure.md). For local testing:

```bash
python mcp_product_server.py  # starts on stdio or SSE
```

### Step 3: Create an agent with Foundry SDK

```bash
pip install azure-ai-projects azure-identity
```

```python
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Get these from your Foundry project settings
PROJECT_CONNECTION_STRING = os.environ["AZURE_AI_PROJECT_CONNECTION_STRING"]

client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=PROJECT_CONNECTION_STRING,
)

# Create the agent
agent = client.agents.create_agent(
    model="gpt-4o-mini",
    name="OutdoorGear Assistant",
    instructions=(
        "You are a helpful customer service agent for OutdoorGear Inc. "
        "Help customers find products, answer policy questions, and assist with orders. "
        "Be friendly, concise, and accurate. "
        "When you don't know something, say so honestly."
    ),
)
print(f"Created agent: {agent.id}")
```

### Step 4: Run a conversation

```python
# Create a thread (conversation session)
thread = client.agents.create_thread()

# Add a user message
client.agents.create_message(
    thread_id=thread.id,
    role="user",
    content="Hi! I'm looking for a tent for a winter camping trip to Mt. Rainier. What do you recommend?"
)

# Run the agent
run = client.agents.create_and_process_run(
    thread_id=thread.id,
    assistant_id=agent.id,
)

print(f"Run status: {run.status}")

# Get the response
messages = client.agents.list_messages(thread_id=thread.id)
for msg in messages.data:
    if msg.role == "assistant":
        for content in msg.content:
            if content.type == "text":
                print(f"\n🤖 {content.text.value}")
```

### Step 5: Add MCP tools to the agent

```python
# For Cloud MCP server (deployed via Lab 028):
agent_with_tools = client.agents.create_agent(
    model="gpt-4o-mini",
    name="OutdoorGear Assistant + Search",
    instructions="You are a helpful outdoor gear assistant. Use the search tool to find products.",
    tools=[
        {
            "type": "mcp",
            "server_label": "outdoorgear",
            "server_url": "https://YOUR-MCP-APP.azurecontainerapps.io/sse",
            "allowed_tools": ["search_products", "get_product", "list_categories"],
        }
    ]
)

# Now the agent can call your MCP server tools automatically
thread2 = client.agents.create_thread()
client.agents.create_message(
    thread_id=thread2.id,
    role="user",
    content="What climbing harnesses are currently in stock?"
)
run2 = client.agents.create_and_process_run(
    thread_id=thread2.id,
    assistant_id=agent_with_tools.id,
)

# Get response (agent will have called MCP tools)
messages2 = client.agents.list_messages(thread_id=thread2.id)
for msg in messages2.data:
    if msg.role == "assistant":
        print(msg.content[0].text.value)
```

---

## Cleanup

```bash
az group delete --name rg-ai-labs-foundry --yes --no-wait
```

---

## Next Steps

- **Add pgvector for RAG:** → [Lab 031 — pgvector on Azure](lab-031-pgvector-semantic-search.md)
- **Row Level Security:** → [Lab 032 — RLS for Agents](lab-032-row-level-security.md)
