# Pré-requisitos e Contas

Esta página informa exatamente quais contas e ferramentas você precisa para cada nível de laboratório — e como obtê-las gratuitamente.

---

## Referência Rápida

| Você tem | Você pode executar |
|----------|-------------------|
| Nada (apenas um navegador) | Laboratórios L50 |
| Conta gratuita do GitHub | Laboratórios L50, L100, L200 |
| Conta gratuita do GitHub + tenant de desenvolvedor M365 | L50–L200 + laboratórios do Teams |
| Teste gratuito do Azure (crédito de $200) | A maioria dos laboratórios L300 |
| Assinatura do Azure (pré-pago) | Todos os laboratórios incluindo L400 |

---

## 1. Conta do GitHub (Gratuita)

**Necessária para:** L100 e acima.

Cadastre-se em [github.com](https://github.com/signup) — é gratuito, sem necessidade de cartão de crédito.

Com uma conta gratuita do GitHub você tem acesso a:

- ✅ **GitHub Copilot Free** — cota de completações e franquia mensal limitada de AI Credits
- ✅ **GitHub Codespaces** — 60 horas/mês de ambiente de desenvolvimento na nuvem gratuito
- ✅ **GitHub Actions** — 2.000 minutos/mês de CI/CD gratuito

!!! info "Elegibilidade estudantil"
    Consulte o [GitHub Student Developer Pack](https://education.github.com/pack) para verificar os benefícios atuais. Este hub não presume que um plano pago do Copilot esteja disponível.

---

## 2. Backend de LLM Local (Grátis)

**Necessário para:** Laboratórios L200 que usam LLMs sem Azure.

Use Foundry Local ou Ollama. Ambos executam na sua máquina e expõem um endpoint compatível com OpenAI.

**Configuração:**

1. Conclua o [Lab 013 — Backends de LLM Gratuitos](labs/lab-013-github-models.md).
2. Configure `LOCAL_LLM_BASE_URL` e `LOCAL_LLM_MODEL`.
3. Mantenha o runtime local ativo durante os labs dependentes.

!!! note "Hardware"
    Modelos pequenos podem executar em CPU. Modelos maiores ou mais rápidos podem exigir GPU/NPU compatível e recebem o selo **GRÁTIS***.

---

## 3. Conta Gratuita do Azure

**Necessária para:** Laboratórios L300.

O Azure oferece uma conta gratuita com:

- ✅ **Crédito de $200** por 30 dias
- ✅ **12 meses** de serviços gratuitos populares
- ✅ Serviços **sempre gratuitos** (inclui alguns de computação, armazenamento, IA)

Cadastre-se em [azure.microsoft.com/free](https://azure.microsoft.com/free) — requer um cartão de crédito para verificação de identidade, mas você não será cobrado durante o período gratuito.

!!! note "Azure para Estudantes"
    Estudantes recebem **crédito de $100** **sem cartão de crédito** pelo [Azure for Students](https://azure.microsoft.com/free/students).

### Serviços do Azure usados nos laboratórios L300

| Serviço | Nível gratuito? | Observações |
|---------|----------------|-------------|
| Azure AI Foundry | ✅ Sim (limitado) | Alguns modelos requerem pré-pago |
| Azure Database for PostgreSQL Flexible Server | ✅ Sim (Burstable B1ms) | Extensão pgvector disponível |
| Azure Container Apps | ✅ Sim (limitado) | Para hospedar servidores MCP |
| Application Insights | ✅ Sim (5GB/mês) | Para laboratórios de observabilidade |

---

## 4. Assinatura do Azure (Pré-pago)

**Necessária para:** Laboratórios L400 e uso mais intenso de L300.

Após seus créditos gratuitos acabarem, você precisará de uma assinatura **pré-pago**.

!!! danger "Fique de olho nos custos"
    Laboratórios L400 usam serviços mais caros. Cada laboratório inclui um custo mensal estimado no topo. Sempre **configure alertas de orçamento** no portal do Azure.

    → [Como configurar um alerta de orçamento no Azure](https://learn.microsoft.com/azure/cost-management-billing/costs/tutorial-acm-create-budgets)

---

## 5. Tenant de Desenvolvedor Microsoft 365 (Opcional)

**Necessário para:** Laboratórios no caminho **Agent Builder — Teams**.

Obtenha uma assinatura gratuita de desenvolvedor M365:

1. Participe do [Microsoft 365 Developer Program](https://developer.microsoft.com/microsoft-365/dev-program) (gratuito)
2. Configure um sandbox instantâneo com 25 licenças de usuário
3. Use-o para laboratórios do Teams AI Library e Copilot Studio

---

## 6. Ferramentas de Desenvolvimento Local

Todos os laboratórios de codificação pressupõem que você tem estas ferramentas instaladas localmente (todas gratuitas):

| Ferramenta | Link de instalação | Laboratórios |
|------------|-------------------|-------------|
| **VS Code** | [code.visualstudio.com](https://code.visualstudio.com) | Todos os laboratórios de codificação |
| **Python 3.11+** | [python.org](https://python.org) | Laboratórios Python |
| **.NET 8 SDK** | [dotnet.microsoft.com](https://dotnet.microsoft.com/download) | Laboratórios C# |
| **Docker Desktop** | [docker.com](https://www.docker.com/products/docker-desktop/) | Laboratórios com PostgreSQL local |
| **Node.js 20+** | [nodejs.org](https://nodejs.org) | Alguns laboratórios MCP |
| **Git** | [git-scm.com](https://git-scm.com) | Todos os laboratórios |

!!! tip "Use GitHub Codespaces para pular a configuração local"
    Muitos laboratórios incluem um botão **Abrir no Codespaces**. Isso fornece um ambiente de desenvolvimento na nuvem totalmente configurado no seu navegador — incluído no nível gratuito do GitHub (60 hrs/mês).

---

## Tabela Resumo

| Nível | Contas necessárias | Custo estimado |
|-------|-------------------|----------------|
| <span class="level-badge level-50">L50</span> | Nenhuma | Gratuito |
| <span class="level-badge level-100">L100</span> | GitHub (gratuito) | Gratuito |
| <span class="level-badge level-200">L200</span> | GitHub (gratuito) | Gratuito |
| <span class="level-badge level-300">L300</span> | GitHub + teste gratuito do Azure | ~$0–$10/laboratório |
| <span class="level-badge level-400">L400</span> | GitHub + Azure pago | ~$10–$50/laboratório |
