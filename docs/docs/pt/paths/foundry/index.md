# 🏭 Trilha Microsoft Foundry

<span class="level-badge level-200">L200</span> <span class="level-badge level-300">L300</span> <span class="level-badge level-400">L400</span>

Microsoft Foundry (Azure AI Foundry) é a plataforma empresarial da Microsoft para construir, implantar e gerenciar agentes de IA em escala. Reúne catálogo de modelos, orquestração de agentes, avaliação, monitoramento e governança em um portal e SDK unificados.

---

## O que Você Vai Construir

Ao final desta trilha você terá:

- ✅ Navegado pelo portal do Azure AI Foundry e implantado um modelo
- ✅ Construído um **Agente de IA** com ferramentas e integração MCP
- ✅ Conectado um **banco de dados PostgreSQL** via MCP para busca semântica
- ✅ Protegido dados com **Row Level Security**
- ✅ Observado e rastreado chamadas de agentes com **Application Insights**
- ✅ Avaliado a qualidade do agente com o **Azure AI Evaluation SDK**

---

## Laboratórios da Trilha (7 laboratórios, ~525 min no total)

| Lab | Título | Nível | Custo |
|-----|--------|-------|-------|
| [Lab 009](../../labs/lab-009-azure-openai.md) | Início Rápido do Azure OpenAI Service | <span class="level-badge level-100">L100</span> | ⚠️ Azure |
| [Lab 030](../../labs/lab-030-foundry-agent-mcp.md) | Microsoft Foundry Agent Service + MCP | <span class="level-badge level-300">L300</span> | Free |
| [Lab 032](../../labs/lab-032-row-level-security.md) | Row Level Security para Agentes | <span class="level-badge level-300">L300</span> | ✅ Free |
| [Lab 033](../../labs/lab-033-agent-observability.md) | Observabilidade de Agentes com Application Insights | <span class="level-badge level-300">L300</span> | ✅ Free |
| [Lab 049](../../labs/lab-049-foundry-iq-agent-tracing.md) | Foundry IQ — Rastreamento de Agentes com OpenTelemetry | <span class="level-badge level-300">L300</span> | ✅ Free |
| [Lab 074](../../labs/lab-074-foundry-agent-service.md) | Foundry Agent Service — Implantação Multi-Agente em Produção | <span class="level-badge level-300">L300</span> | ✅ Free |
| [Lab 050](../../labs/lab-050-multi-agent-observability.md) | Observabilidade Multi-Agente com Convenções Semânticas GenAI | <span class="level-badge level-400">L400</span> | ✅ Free |

---

## Componentes Principais do Microsoft Foundry

| Componente | Descrição |
|------------|-----------|
| **Model Catalog** | Mais de 1.800 modelos incluindo OpenAI, Meta, Mistral, Cohere |
| **Agent Service** | Runtime gerenciado para agentes com chamada de ferramentas, interpretador de código, MCP |
| **Evaluation SDK** | Métricas de qualidade: fundamentação, coerência, relevância, segurança |
| **Azure Monitor** | Rastreamento distribuído, métricas, integração com Application Insights |
| **Content Safety** | Proteções de IA responsável integradas |

---

## Pré-requisitos

!!! warning "Assinatura do Azure necessária"
    Todos os laboratórios desta trilha requerem uma assinatura do Azure.  
    → [Configure sua conta Azure](../../prerequisites.md)

---

## Recursos Externos

- [Documentação do Microsoft Foundry](https://learn.microsoft.com/azure/ai-foundry/)
- [Azure AI Agent Service](https://learn.microsoft.com/azure/ai-services/agents/)
- [Azure AI Evaluation SDK](https://learn.microsoft.com/azure/ai-foundry/how-to/develop/agent-evaluate-sdk)
- [Rastreamento com App Insights](https://learn.microsoft.com/azure/ai-services/agents/concepts/tracing)
