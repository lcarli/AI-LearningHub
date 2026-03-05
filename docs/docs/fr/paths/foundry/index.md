# 🏭 Parcours Microsoft Foundry

<span class="level-badge level-200">L200</span> <span class="level-badge level-300">L300</span> <span class="level-badge level-400">L400</span>

Microsoft Foundry (Azure AI Foundry) est la plateforme d'entreprise de Microsoft pour construire, déployer et gérer des agents IA à grande échelle. Elle rassemble le catalogue de modèles, l'orchestration d'agents, l'évaluation, la surveillance et la gouvernance dans un portail et un SDK unifiés.

---

## Ce que Vous Allez Construire

À la fin de ce parcours, vous aurez :

- ✅ Navigué dans le portail Azure AI Foundry et déployé un modèle
- ✅ Construit un **Agent IA** avec des outils et une intégration MCP
- ✅ Connecté une **base de données PostgreSQL** via MCP pour la recherche sémantique
- ✅ Sécurisé les données avec le **Row Level Security**
- ✅ Observé et tracé les appels d'agents avec **Application Insights**
- ✅ Évalué la qualité de l'agent avec le **Azure AI Evaluation SDK**

---

## Laboratoires du Parcours (7 laboratoires, ~525 min au total)

| Lab | Titre | Niveau | Coût |
|-----|-------|--------|------|
| [Lab 009](../../labs/lab-009-azure-openai.md) | Démarrage Rapide Azure OpenAI Service | <span class="level-badge level-100">L100</span> | ⚠️ Azure |
| [Lab 030](../../labs/lab-030-foundry-agent-mcp.md) | Microsoft Foundry Agent Service + MCP | <span class="level-badge level-300">L300</span> | Free |
| [Lab 032](../../labs/lab-032-row-level-security.md) | Row Level Security pour les Agents | <span class="level-badge level-300">L300</span> | ✅ Free |
| [Lab 033](../../labs/lab-033-agent-observability.md) | Observabilité des Agents avec Application Insights | <span class="level-badge level-300">L300</span> | ✅ Free |
| [Lab 049](../../labs/lab-049-foundry-iq-agent-tracing.md) | Foundry IQ — Traçage d'Agents avec OpenTelemetry | <span class="level-badge level-300">L300</span> | ✅ Free |
| [Lab 074](../../labs/lab-074-foundry-agent-service.md) | Foundry Agent Service — Déploiement Multi-Agent en Production | <span class="level-badge level-300">L300</span> | ✅ Free |
| [Lab 050](../../labs/lab-050-multi-agent-observability.md) | Observabilité Multi-Agent avec les Conventions Sémantiques GenAI | <span class="level-badge level-400">L400</span> | ✅ Free |

---

## Composants Clés de Microsoft Foundry

| Composant | Description |
|-----------|-------------|
| **Model Catalog** | Plus de 1 800 modèles incluant OpenAI, Meta, Mistral, Cohere |
| **Agent Service** | Runtime géré pour agents avec appel d'outils, interpréteur de code, MCP |
| **Evaluation SDK** | Métriques de qualité : ancrage, cohérence, pertinence, sécurité |
| **Azure Monitor** | Traçage distribué, métriques, intégration Application Insights |
| **Content Safety** | Garde-fous d'IA responsable intégrés |

---

## Prérequis

!!! warning "Abonnement Azure requis"
    Tous les laboratoires de ce parcours nécessitent un abonnement Azure.  
    → [Configurez votre compte Azure](../../prerequisites.md)

---

## Ressources Externes

- [Documentation Microsoft Foundry](https://learn.microsoft.com/azure/ai-foundry/)
- [Azure AI Agent Service](https://learn.microsoft.com/azure/ai-services/agents/)
- [Azure AI Evaluation SDK](https://learn.microsoft.com/azure/ai-foundry/how-to/develop/agent-evaluate-sdk)
- [Traçage avec App Insights](https://learn.microsoft.com/azure/ai-services/agents/concepts/tracing)
