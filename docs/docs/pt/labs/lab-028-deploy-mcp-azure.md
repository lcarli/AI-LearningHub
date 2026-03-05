---
tags: [mcp, azure, container-apps, bicep, azure-required]
---
# Lab 028: Implantar Servidor MCP no Azure Container Apps

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/mcp/">MCP</a></span>
  <span><strong>Tempo:</strong> ~60 min</span>
  <span><strong>💰 Custo:</strong> ~$0 (scale-to-zero) + Azure Container Registry ~$5/month</span>
</div>

!!! warning "Assinatura Azure necessária"
    Este lab implanta Azure Container Apps. → [Guia de pré-requisitos](../prerequisites.md)

## O que Você Vai Aprender

- Containerizar um servidor MCP (Python) com Docker
- Enviar a imagem para o **Azure Container Registry**
- Implantar no **Azure Container Apps** com transporte SSE
- Atualizar o servidor MCP com deploys de atualização contínua sem tempo de inatividade
- Conectar a partir do GitHub Copilot e qualquer cliente MCP

---

## Pré-requisitos

- Docker Desktop — gratuito: https://www.docker.com/products/docker-desktop
- Azure CLI: `az login`
- Ter completado o [Lab 020 — Servidor MCP em Python](lab-020-mcp-server-python.md)

---

## Implantar Infraestrutura

### Opção A — Implantar no Azure (um clique)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Flcarli%2FAI-LearningHub%2Fmain%2Finfra%2Flab-028-mcp-container-apps%2Fazuredeploy.json)

Isto implanta:
- Ambiente Azure Container Apps + Log Analytics
- Um container app placeholder (você o atualizará com sua imagem no Passo 3)

### Opção B — Azure CLI (Bicep)

```bash
git clone https://github.com/lcarli/AI-LearningHub.git && cd AI-LearningHub

az group create --name rg-ai-labs-mcp --location eastus

az deployment group create \
  --resource-group rg-ai-labs-mcp \
  --template-file infra/lab-028-mcp-container-apps/main.bicep

# Get the app URL
az deployment group show \
  --resource-group rg-ai-labs-mcp \
  --name main \
  --query properties.outputs.appUrl.value -o tsv
```

---

## Exercício do Lab

### Passo 1: Criar o servidor MCP (transporte SSE)

Para implantação remota, use transporte SSE (Server-Sent Events) em vez de stdio.

```
mcp-product-server/
├── server.py
├── Dockerfile
└── requirements.txt
```

**`server.py`**:

```python
import os, csv, json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("OutdoorGear Product Server")

# Load product catalog from GitHub raw URL or local file
PRODUCTS_URL = "https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/products.csv"

import urllib.request, io

def load_products() -> list[dict]:
    with urllib.request.urlopen(PRODUCTS_URL) as r:
        content = r.read().decode("utf-8")
    return list(csv.DictReader(io.StringIO(content)))

PRODUCTS = load_products()

@mcp.tool()
def search_products(query: str) -> str:
    """Search outdoor gear products by keyword."""
    q = query.lower()
    matches = [
        p for p in PRODUCTS
        if q in p["name"].lower() or q in p["category"].lower() or q in p["description"].lower()
    ]
    if not matches:
        return "No products found."
    return json.dumps(matches[:5], indent=2)

@mcp.tool()
def get_product(sku: str) -> str:
    """Get full details for a product by SKU."""
    for p in PRODUCTS:
        if p["sku"].lower() == sku.lower():
            return json.dumps(p, indent=2)
    return f"Product with SKU '{sku}' not found."

@mcp.tool()
def list_categories() -> str:
    """List all available product categories."""
    cats = sorted(set(f"{p['category']}/{p['subcategory']}" for p in PRODUCTS))
    return "\n".join(cats)

if __name__ == "__main__":
    # Use SSE transport for remote/cloud deployment
    mcp.run(transport="sse", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
```

**`requirements.txt`**:
```
mcp[cli]>=1.0.0
```

**`Dockerfile`**:
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py .
EXPOSE 8000
CMD ["python", "server.py"]
```

### Passo 2: Testar localmente

```bash
cd mcp-product-server
pip install mcp
python server.py
# Server running on http://0.0.0.0:8000

# Test in another terminal
npx @modelcontextprotocol/inspector http://localhost:8000/sse
```

### Passo 3: Construir e enviar a imagem do container

```bash
# Variables — update these
RESOURCE_GROUP="rg-ai-labs-mcp"
ACR_NAME="mcpacr$(date +%s | tail -c 6)"   # unique name

# Create Azure Container Registry (Basic tier ~$5/month)
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic

# Build and push
az acr build --registry $ACR_NAME --image mcp-product-server:latest .

# Get the image URL
IMAGE_URL="${ACR_NAME}.azurecr.io/mcp-product-server:latest"
echo "Image: $IMAGE_URL"
```

### Passo 4: Implantar no Container Apps

```bash
# Get the app name from deployment outputs
APP_NAME=$(az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name main \
  --query properties.outputs.appName.value -o tsv)

ENV_NAME=$(az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name main \
  --query properties.outputs.environmentName.value -o tsv)

# Enable Container Apps to pull from ACR
az containerapp registry set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --server "${ACR_NAME}.azurecr.io" \
  --identity system

# Update the container app with your image
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --image $IMAGE_URL

# Get the public URL
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv
```

### Passo 5: Conectar a partir do GitHub Copilot

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "outdoorgear-cloud": {
      "type": "sse",
      "url": "https://YOUR-APP-NAME.YOUR-REGION.azurecontainerapps.io/sse"
    }
  }
}
```

Teste no Copilot Agent Mode: *"Quais barracas de camping vocês têm em estoque?"*

### Passo 6: Atualizações sem tempo de inatividade

```bash
# Update to a new version
az acr build --registry $ACR_NAME --image mcp-product-server:v2 .

az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --image "${ACR_NAME}.azurecr.io/mcp-product-server:v2"

# Container Apps performs a rolling update automatically
```

---

## Detalhamento de Custos

| Recurso | SKU | Custo Estimado |
|---------|-----|----------------|
| Container Apps | Scale-to-zero (0 replicas when idle) | ~$0 when idle |
| Container Apps (active) | 0.5 vCPU / 1Gi | ~$0.02/hour active |
| Azure Container Registry | Basic | ~$5/month |
| Log Analytics | PerGB2018 | ~$2/month (light usage) |

!!! tip "Escalar até zero"
    O Container Apps escala para 0 réplicas quando não há requisições. Para um servidor MCP de dev/lab com uso ocasional, você pagará quase nada.

---

## Limpeza

```bash
az group delete --name rg-ai-labs-mcp --yes --no-wait
```

---

## Próximos Passos

- **Proteger o servidor com autenticação:** Adicione Azure API Management ou Easy Auth na frente
- **Pipeline completo Foundry + MCP:** → [Lab 030 — Foundry Agent Service + MCP](lab-030-foundry-agent-mcp.md)
