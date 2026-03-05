---
tags: [mcp, azure, container-apps, bicep, azure-required]
---
# Lab 028 : Déployer un serveur MCP sur Azure Container Apps

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/mcp/">MCP</a></span>
  <span><strong>Durée :</strong> ~60 min</span>
  <span><strong>💰 Coût :</strong> ~0 $ (mise à l'échelle à zéro) + Azure Container Registry ~5 $/mois</span>
</div>

!!! warning "Abonnement Azure requis"
    Ce lab déploie Azure Container Apps. → [Guide des prérequis](../prerequisites.md)

## Ce que vous apprendrez

- Conteneuriser un serveur MCP (Python) avec Docker
- Pousser l'image vers **Azure Container Registry**
- Déployer sur **Azure Container Apps** avec le transport SSE
- Mettre à jour le serveur MCP avec des déploiements progressifs sans interruption
- Se connecter depuis GitHub Copilot et tout client MCP

---

## Prérequis

- Docker Desktop — gratuit : https://www.docker.com/products/docker-desktop
- Azure CLI : `az login`
- Avoir terminé le [Lab 020 — Serveur MCP en Python](lab-020-mcp-server-python.md)

---

## Déployer l'infrastructure

### Option A — Déployer sur Azure (un clic)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Flcarli%2FAI-LearningHub%2Fmain%2Finfra%2Flab-028-mcp-container-apps%2Fazuredeploy.json)

Ceci déploie :
- Environnement Azure Container Apps + Log Analytics
- Une application conteneur de substitution (vous la mettrez à jour avec votre image à l'étape 3)

### Option B — Azure CLI (Bicep)

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

## Exercice du lab

### Étape 1 : Créer le serveur MCP (transport SSE)

Pour le déploiement distant, utilisez le transport SSE (Server-Sent Events) au lieu de stdio.

```
mcp-product-server/
├── server.py
├── Dockerfile
└── requirements.txt
```

**`server.py`** :

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

**`requirements.txt`** :
```
mcp[cli]>=1.0.0
```

**`Dockerfile`** :
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py .
EXPOSE 8000
CMD ["python", "server.py"]
```

### Étape 2 : Tester localement

```bash
cd mcp-product-server
pip install mcp
python server.py
# Server running on http://0.0.0.0:8000

# Test in another terminal
npx @modelcontextprotocol/inspector http://localhost:8000/sse
```

### Étape 3 : Construire et pousser l'image conteneur

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

### Étape 4 : Déployer sur Container Apps

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

### Étape 5 : Se connecter depuis GitHub Copilot

Ajoutez à `.vscode/mcp.json` :

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

Testez en mode Agent Copilot : *« Quelles tentes de camping avez-vous en stock ? »*

### Étape 6 : Mises à jour sans interruption

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

## Détail des coûts

| Ressource | SKU | Coût estimé |
|-----------|-----|-------------|
| Container Apps | Mise à l'échelle à zéro (0 réplicas au repos) | ~0 $ au repos |
| Container Apps (actif) | 0.5 vCPU / 1 Gio | ~0,02 $/heure actif |
| Azure Container Registry | Basic | ~5 $/mois |
| Log Analytics | PerGB2018 | ~2 $/mois (utilisation légère) |

!!! tip "Mise à l'échelle à zéro"
    Container Apps met à l'échelle à 0 réplicas lorsqu'il n'y a pas de requêtes. Pour un serveur MCP de développement/lab avec une utilisation occasionnelle, vous ne paierez presque rien.

---

## Nettoyage

```bash
az group delete --name rg-ai-labs-mcp --yes --no-wait
```

---

## Prochaines étapes

- **Sécuriser le serveur avec l'authentification :** Ajoutez Azure API Management ou Easy Auth en amont
- **Pipeline complet Foundry + MCP :** → [Lab 030 — Foundry Agent Service + MCP](lab-030-foundry-agent-mcp.md)
