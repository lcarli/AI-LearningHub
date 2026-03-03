# Infrastructure Templates

Bicep and ARM JSON templates for deploying Azure resources used in the labs.

## Templates

| Directory | Lab | Resources Created | Estimated Cost |
|-----------|-----|-------------------|---------------|
| `lab-028-mcp-container-apps/` | [Lab 028](../docs/docs/en/labs/lab-028-deploy-mcp-azure.md) | Container Apps Environment + App, Log Analytics | ~$0 (scale-to-zero) |
| `lab-030-foundry/` | [Lab 030](../docs/docs/en/labs/lab-030-foundry-agent-mcp.md) | AI Foundry Hub + Project, Storage, Key Vault | ~$5–10/month |
| `lab-031-pgvector/` | [Lab 031](../docs/docs/en/labs/lab-031-pgvector-semantic-search.md) | PostgreSQL Flexible Server (Burstable B1ms) + pgvector | ~$15/month |

## Deploy to Azure

### Lab 031 — pgvector on Azure

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Flcarli%2FAI-LearningHub%2Fmain%2Finfra%2Flab-031-pgvector%2Fazuredeploy.json)

### Lab 028 — MCP Server on Container Apps

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Flcarli%2FAI-LearningHub%2Fmain%2Finfra%2Flab-028-mcp-container-apps%2Fazuredeploy.json)

### Lab 030 — Azure AI Foundry

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Flcarli%2FAI-LearningHub%2Fmain%2Finfra%2Flab-030-foundry%2Fazuredeploy.json)

## Deploying with Azure CLI

```bash
# Create a resource group first
az group create --name rg-ai-labs --location eastus

# Lab 031: pgvector
az deployment group create \
  --resource-group rg-ai-labs \
  --template-file infra/lab-031-pgvector/main.bicep \
  --parameters administratorLoginPassword="YourP@ssword123"

# Lab 028: Container Apps
az deployment group create \
  --resource-group rg-ai-labs \
  --template-file infra/lab-028-mcp-container-apps/main.bicep

# Lab 030: AI Foundry
az deployment group create \
  --resource-group rg-ai-labs \
  --template-file infra/lab-030-foundry/main.bicep \
  --parameters location=eastus
```

## Cleanup

```bash
# Delete all lab resources
az group delete --name rg-ai-labs --yes --no-wait
```
