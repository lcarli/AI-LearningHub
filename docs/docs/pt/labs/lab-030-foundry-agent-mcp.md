---
tags: [foundry, mcp, azure, azure-required]
---
# Lab 030: Microsoft Foundry Agent Service + MCP

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/foundry/">Foundry + MCP</a></span>
  <span><strong>Tempo:</strong> ~90 min</span>
  <span><strong>💰 Custo:</strong> Assinatura Azure — custos de token gpt-4o-mini</span>
</div>

!!! warning "Assinatura Azure necessária"
    Este lab requer uma assinatura Azure. → [Guia de pré-requisitos](../prerequisites.md)

## O que Você Vai Aprender

- Implantar o **Azure AI Foundry** Hub + Projeto com um clique
- Implantar um endpoint de modelo **gpt-4o-mini**
- Criar um **Agente** no Foundry Agent Service
- Conectar seu servidor MCP como uma ferramenta para o agente
- Executar uma conversa completa do agente com chamadas de ferramentas

---

## Implantar Infraestrutura

### Opção A — Implantar no Azure (um clique)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Flcarli%2FAI-LearningHub%2Fmain%2Finfra%2Flab-030-foundry%2Fazuredeploy.json)

Isto implanta:
- Azure AI Foundry Hub
- AI Project (OutdoorGear Agent Project)
- Storage Account + Key Vault (necessários pelo Foundry)

!!! tip "Localização recomendada"
    Use **East US** ou **Sweden Central** para melhor disponibilidade de modelos.

### Opção B — Azure CLI (Bicep)

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

## Exercício do Lab

### Passo 1: Implantar gpt-4o-mini no Foundry

1. Acesse [ai.azure.com](https://ai.azure.com) → seu projeto
2. **Model catalog** → search `gpt-4o-mini` → **Deploy**
3. Name: `gpt-4o-mini` — keep defaults
4. Copie a **URL do endpoint** e a **chave de API** da página de implantação

### Passo 2: Iniciar seu servidor MCP

Use o servidor do [Lab 020](lab-020-mcp-server-python.md) ou [Lab 028](lab-028-deploy-mcp-azure.md). Para testes locais:

```bash
python mcp_product_server.py  # starts on stdio or SSE
```

### Passo 3: Criar um agente com o SDK do Foundry

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

### Passo 4: Executar uma conversa

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

### Passo 5: Adicionar ferramentas MCP ao agente

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

## Limpeza

```bash
az group delete --name rg-ai-labs-foundry --yes --no-wait
```

---

## Próximos Passos

- **Adicionar pgvector para RAG:** → [Lab 031 — pgvector on Azure](lab-031-pgvector-semantic-search.md)
- **Row Level Security:** → [Lab 032 — RLS for Agents](lab-032-row-level-security.md)
