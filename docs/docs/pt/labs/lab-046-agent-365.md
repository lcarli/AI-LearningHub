---
tags: [enterprise, microsoft-365, agent-governance, pro-code, mcp, observability]
---
# Lab 046: Microsoft Agent 365 — Governança de Agentes Empresariais

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/pro-code/">⚙️ Pro Code</a></span>
  <span><strong>Tempo:</strong> ~75 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-azure">Pago — Licença Microsoft 365 Copilot + assinatura Azure + programa Frontier</span></span>
</div>

## O que Você Vai Aprender

- O que é o Microsoft Agent 365 e como ele difere de *frameworks* de agentes
- Como o Agent 365 dá a cada agente de IA sua própria **Identidade de Agente Entra**
- Como instalar e configurar a **CLI do Agent 365**
- Como criar um **Agent Blueprint** (o modelo de governança empresarial)
- Como adicionar **observabilidade (OpenTelemetry)** a um agente Python existente usando o SDK do Agent 365
- Como **publicar um agente** no Centro de Administração do Microsoft 365
- Como criar uma **instância de agente** que aparece no organograma no Teams

---

## Introdução

A maioria dos frameworks de agentes de IA foca em *construir* agentes — como eles raciocinam, chamam ferramentas e lembram o contexto. O **Microsoft Agent 365** resolve um problema diferente: **como as empresas governam, protegem e gerenciam agentes em escala?**

Pense no Agent 365 como o *plano de controle* para agentes de IA no seu tenant do Microsoft 365:

![Agent 365 Control Plane](../../assets/diagrams/agent-365-control-plane.svg)

Um agente aprimorado com o Agent 365 obtém:

| Capacidade | O que significa |
|-----------|--------------|
| **Entra Agent ID** | Sua própria identidade no Azure AD — como uma conta de usuário, mas para um agente |
| **Blueprint** | Modelo aprovado pelo TI definindo capacidades, permissões MCP e políticas de governança |
| **Notificações** | Pode receber e responder a @menções no Teams, e-mails, comentários no Word |
| **Ferramentas MCP Governadas** | Acesso a Mail, Calendar, Teams, SharePoint sob controle administrativo |
| **Observabilidade** | Rastreamentos completos via OpenTelemetry de cada chamada de ferramenta e inferência LLM |

!!! warning "Programa preview obrigatório"
    O Microsoft Agent 365 está em **preview Frontier**. Você precisa participar do [Microsoft Copilot Frontier Program](https://adoption.microsoft.com/copilot/frontier-program/) e ter pelo menos uma licença **Microsoft 365 Copilot** no seu tenant.

---

## Arquitetura: Camadas do Agent 365

![Agent 365 Layered Architecture](../../assets/diagrams/agent-365-layers.svg)

O SDK do Agent 365 fica *acima* do seu framework de agentes. Ele **não** o substitui — ele envolve e aprimora.

---

## Pré-requisitos

- [ ] **Licença Microsoft 365 Copilot** (pelo menos 1 no seu tenant)
- [ ] **Acesso ao programa Frontier** — [inscreva-se aqui](https://adoption.microsoft.com/copilot/frontier-program/)
- [ ] **Assinatura Azure** — direitos de criação de recursos
- [ ] **Permissões Entra ID** — Administrador Global, Administrador de ID de Agente ou função de Desenvolvedor de ID de Agente
- [ ] **.NET 8.0 ou posterior** — para a CLI do Agent 365
- [ ] **Python 3.11+** e pip
- [ ] **Token GitHub Models** (gratuito) — para o agente OutdoorGear que vamos aprimorar

!!! tip "Sem acesso ao Frontier? Acompanhe mesmo assim"
    Se você ainda não tem acesso ao Frontier, pode seguir os Passos 1–4 localmente com ferramentas simuladas. O arquivo inicial inclui um modo simulado. Os Passos 5–7 requerem um tenant real.

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Suporte

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-046/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|------|-------------|----------|
| `a365.config.sample.json` | Arquivo de configuração / dados | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-046/a365.config.sample.json) |
| `broken_observability.py` | Exercício de correção de bugs (3 bugs + auto-testes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-046/broken_observability.py) |
| `outdoorgear_a365_starter.py` | Script inicial com TODOs | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-046/outdoorgear_a365_starter.py) |

---

## Passo 1: Instalar a CLI do Agent 365

A CLI do Agent 365 (`a365`) é a espinha dorsal de linha de comando para todo o ciclo de vida de desenvolvimento de agentes.

```bash
# Install (requires .NET 8.0+)
dotnet tool install --global Microsoft.Agents.A365.DevTools.Cli --prerelease

# Verify installation
a365 -h
```

Saída esperada:
```
Microsoft Agent 365 CLI
Version: x.x.x-preview

Usage: a365 [command] [options]

Commands:
  config      Manage Agent 365 configuration
  setup       Set up agent blueprint and Azure resources
  deploy      Deploy agent code to Azure
  publish     Publish agent to Microsoft 365 admin center
  ...
```

!!! note "Sempre use --prerelease"
    Até que o Agent 365 seja GA, sempre inclua `--prerelease` nos comandos de instalação/atualização. Sem isso, o pacote não será encontrado nos feeds do NuGet.

---

## Passo 2: Registrar um Aplicativo Cliente Personalizado no Entra ID

A CLI precisa de seu próprio registro de aplicativo Entra para autenticar contra o seu tenant.

**No Portal Azure → Entra ID → Registros de aplicativo:**

1. Clique em **Novo registro**
2. Nome: `Agent365-CLI-App`
3. Tipos de conta suportados: **Contas apenas neste diretório organizacional**
4. Clique em **Registrar**
5. Copie o **ID do Aplicativo (cliente)** — você precisará dele no Passo 3
6. Vá para **Permissões de API → Adicionar uma permissão → Microsoft Graph**
7. Adicione estas **Permissões de aplicativo**:
   - `AgentLifecycle.ReadWrite.All`
   - `Application.ReadWrite.All`
8. Clique em **Conceder consentimento do administrador**

```bash
# Verify you can authenticate
az login --tenant YOUR_TENANT_ID
```

---

## Passo 3: Inicializar a Configuração do Agent 365

```bash
# Create a new Agent 365 config
a365 config init
```

A CLI solicitará:
- ID do Tenant
- ID da assinatura Azure
- Nome do grupo de recursos
- O ID do aplicativo cliente do Passo 2
- A URL do endpoint de mensagens do seu agente

Isso cria um arquivo `a365.config.json` no diretório do seu projeto:

```json
{
  "tenantId": "YOUR_TENANT_ID",
  "subscriptionId": "YOUR_SUBSCRIPTION_ID",
  "resourceGroup": "rg-outdoorgear-agent",
  "clientAppId": "YOUR_CLIENT_APP_ID",
  "agentMessagingEndpoint": "https://your-agent.azurewebsites.net/api/messages",
  "agentBlueprintName": "OutdoorGearAgent",
  "mcpPermissions": [
    "mail.read",
    "calendar.readwrite",
    "teams.message.send"
  ]
}
```

!!! tip "Use o config de exemplo"
    O lab inclui `lab-046/a365.config.sample.json` como referência. Copie-o, preencha seus valores e renomeie para `a365.config.json`.

---

## Passo 4: Adicionar o SDK do Agent 365 ao Seu Agente Python

Instale os pacotes do SDK do Agent 365:

```bash
pip install openai \
  microsoft-agents-a365-observability-core \
  microsoft-agents-a365-observability-extensions-openai \
  microsoft-agents-a365-notifications \
  microsoft-agents-a365-tooling \
  microsoft-agents-a365-tooling-extensions-openai
```

### 4a. Adicionar Observabilidade (OpenTelemetry)

O SDK instrumenta seu agente automaticamente para o OpenAI Agents SDK:

```python
from openai import AsyncOpenAI
from agents import Agent, Runner
from microsoft.agents.a365.observability.core import A365ObservabilityProvider
from microsoft.agents.a365.observability.extensions.openai import OpenAIAgentInstrumentation

# Initialize observability
observability = A365ObservabilityProvider(
    service_name="OutdoorGearAgent",
    service_version="1.0.0",
    exporter_endpoint="https://your-otel-collector.endpoint"
)

# Auto-instrument the OpenAI Agents SDK
instrumentation = OpenAIAgentInstrumentation(provider=observability)
instrumentation.instrument()

# Every agent run is now traced automatically!
```

### 4b. Adicionar Ferramentas MCP Governadas

Conecte-se aos servidores MCP do Microsoft 365 (Mail, Calendar, Teams) sob controle administrativo:

```python
from microsoft.agents.a365.tooling import A365ToolingClient
from microsoft.agents.a365.tooling.extensions.openai import OpenAIMcpRegistrationService

async def setup_m365_tools(agent: Agent) -> Agent:
    """Register governed M365 MCP tools to an existing agent."""
    
    tooling_client = A365ToolingClient(
        agent_id="YOUR_ENTRA_AGENT_ID",
        tenant_id="YOUR_TENANT_ID"
    )
    
    # Get available governed MCP servers for this agent
    mcp_servers = await tooling_client.get_mcp_servers()
    
    # Register with OpenAI Agents SDK
    registration_service = OpenAIMcpRegistrationService(agent)
    for server in mcp_servers:
        await registration_service.register(server)
    
    return agent
```

### 4c. Adicionar Notificações (Teams / Outlook)

Faça seu agente responder a @menções e e-mails:

```python
from microsoft.agents.a365.notifications import A365NotificationHandler

class OutdoorGearNotificationHandler(A365NotificationHandler):
    
    async def on_teams_mention(self, context):
        """Called when @OutdoorGearAgent is mentioned in Teams."""
        user_message = context.activity.text
        # Pass to your agent's run loop
        response = await Runner.run(
            self.agent,
            input=user_message,
            context=context
        )
        await context.send_activity(response.final_output)
    
    async def on_email_received(self, context):
        """Called when agent mailbox receives an email."""
        subject = context.activity.subject
        body = context.activity.body
        # Handle email queries
        response = await Runner.run(
            self.agent,
            input=f"Email subject: {subject}\n\n{body}"
        )
        await context.reply_to_email(response.final_output)
```

---

## Passo 5: Criar o Agent Blueprint

O blueprint é o modelo empresarial aprovado pelo TI para o seu agente. Crie-o com um único comando CLI:

```bash
a365 setup
```

Este comando:
1. Cria um **Azure Entra Agent ID** (service principal para o seu agente)
2. Registra as **permissões de ferramentas MCP** do agente conforme definido em `a365.config.json`
3. Cria o **Agent Blueprint** no Azure
4. Retorna um `blueprintId` que você precisará para publicação

```
✅ Agent identity created: OutdoorGearAgent (ID: agt-12345-...)
✅ MCP permissions registered: mail.read, calendar.readwrite, teams.message.send
✅ Blueprint created: OutdoorGearAgent-Blueprint-v1
   Blueprint ID: bpnt-67890-...
```

---

## Passo 6: Implantar o Código do Agente no Azure

Se você não tem uma implantação Azure existente:

```bash
# Deploy to Azure App Service
a365 deploy --target azure-app-service --resource-group rg-outdoorgear-agent

# Or deploy to Azure Container Apps
a365 deploy --target azure-container-apps --resource-group rg-outdoorgear-agent
```

Seu agente deve estar acessível na URL do endpoint de mensagens que você definiu em `a365.config.json`.

---

## Passo 7: Publicar no Centro de Administração do Microsoft 365

```bash
a365 publish --blueprint-id bpnt-67890-...
```

Após a publicação:

1. Vá para o [Centro de Administração do Microsoft 365](https://admin.microsoft.com) → **Agentes**
2. Encontre o **OutdoorGearAgent** no registro
3. Clique em **Criar instância** para instanciar o agente para sua organização
4. O agente recebe:
   - Sua própria entrada no organograma
   - Um endereço de e-mail (`outdoorgear-agent@yourorg.com`)
   - Capacidade de ser @mencionado no Teams
   - Visibilidade no **Mapa de Agentes** (quem o usa, quais dados ele acessa)

!!! info "O agente aparece no Teams em minutos"
    Após criar uma instância, seu agente aparece na busca do Teams. Os usuários podem @mencioná-lo em chats e canais. Ele também aparece nos contatos do Outlook.

---

## 🐛 Exercício de Correção de Bugs: Corrigir a Configuração de Observabilidade Quebrada

O lab inclui uma configuração de observabilidade quebrada. Encontre e corrija 3 bugs!

```
lab-046/
└── broken_observability.py    ← 3 bugs intencionais para encontrar e corrigir
```

**Configuração:**
```bash
pip install microsoft-agents-a365-observability-core \
            microsoft-agents-a365-observability-extensions-openai

python lab-046/broken_observability.py
```

**Os 3 bugs:**

| # | Componente | Sintoma | Tipo |
|---|-----------|---------|------|
| 1 | `A365ObservabilityProvider` | `TypeError: missing required argument 'service_name'` | Parâmetro obrigatório ausente |
| 2 | `OpenAIAgentInstrumentation` | Traces mostram `service_name: unknown` em vez de `OutdoorGearAgent` | Provider não passado para a instrumentação |
| 3 | Endpoint do exportador | `ConnectionRefusedError: localhost:4317` | Endpoint errado — deve usar coletor HTTPS |

**Verifique suas correções:** Após corrigir todos os 3 bugs, execute:
```bash
python lab-046/broken_observability.py
# Expected:
# ✅ ObservabilityProvider initialized: OutdoorGearAgent v1.0.0
# ✅ Instrumentation active — traces will include service_name: OutdoorGearAgent
# ✅ Exporter endpoint validated: https://...
# 🎉 Observability configured correctly!
```

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Um agente construído com LangChain quer usar o Microsoft Agent 365. O que o Agent 365 fornece que o LangChain NÃO fornece?"

    - A) A capacidade de chamar APIs e ferramentas externas
    - B) Raciocínio e planejamento em múltiplos passos
    - C) Identidade respaldada pelo Entra, ferramentas MCP governadas, observabilidade e governança/conformidade empresarial
    - D) Um modelo LLM melhor para raciocínio

    ??? success "✅ Revelar Resposta"
        **Correto: C**

        O Agent 365 NÃO é um framework de agentes — ele não ajuda a construir lógica de raciocínio. O LangChain já lida com chamadas de ferramentas, raciocínio em múltiplos passos e planejamento. O que o Agent 365 adiciona é a **camada empresarial**: uma identidade Entra única para o agente, acesso MCP governado e aprovado pelo TI para cargas de trabalho do M365, observabilidade OpenTelemetry, governança baseada em blueprints e a capacidade dos administradores de TI verem, monitorarem e controlarem o agente a partir do Centro de Administração do M365.

??? question "**Q2 (Múltipla Escolha):** O que é um Agent Blueprint no Microsoft Agent 365?"

    - A) Um modelo Bicep/ARM para implantar recursos Azure
    - B) Um modelo pré-configurado e aprovado pelo TI que define as capacidades do agente, permissões MCP, políticas de governança e restrições de conformidade
    - C) Uma classe Python que todos os agentes do Agent 365 devem herdar
    - D) Um diagrama do fluxo de chamadas de ferramentas do agente

    ??? success "✅ Revelar Resposta"
        **Correto: B**

        Um blueprint vem do Microsoft Entra e é o *modelo empresarial* a partir do qual instâncias de agentes conformes são criadas. Ele define o que o agente pode fazer (capacidades), quais dados do M365 ele pode acessar (permissões MCP), como ele é governado (políticas DLP, restrições de acesso externo, regras de log) e metadados de ciclo de vida. Cada instância de agente criada a partir do blueprint herda todas essas regras — garantindo que não haja "agentes sombra" com acesso descontrolado.

??? question "**Q3 (Execute o Lab):** Abra `lab-046/outdoorgear_a365_starter.py`. Quantos comentários TODO existem no arquivo?"

    Abra o arquivo inicial e conte os marcadores `# TODO`.

    ??? success "✅ Revelar Resposta"
        **5 TODOs**

        O arquivo inicial tem 5 pontos de integração para você completar:
        1. TODO 1: Inicializar `A365ObservabilityProvider` com nome e versão do serviço
        2. TODO 2: Aplicar `OpenAIAgentInstrumentation` para auto-instrumentar traces
        3. TODO 3: Implementar o handler `on_teams_mention`
        4. TODO 4: Conectar aos servidores de ferramentas MCP governadas
        5. TODO 5: Registrar o Entra Agent ID do agente

??? question "**Q4 (Múltipla Escolha):** Um usuário @menciona seu Agente OutdoorGear em um canal do Teams. Qual componente do SDK do Agent 365 recebe e roteia essa notificação para o código do seu agente?"

    - A) `A365ObservabilityProvider`
    - B) `A365ToolingClient`
    - C) `A365NotificationHandler`
    - D) `OpenAIMcpRegistrationService`

    ??? success "✅ Revelar Resposta"
        **Correto: C — `A365NotificationHandler`**

        O `A365NotificationHandler` recebe eventos de aplicativos do Microsoft 365 — @menções no Teams, e-mails recebidos na caixa de correio do agente, notificações de comentários no Word e muito mais. Você cria uma subclasse dele e sobrescreve métodos como `on_teams_mention()` e `on_email_received()`. O `A365ObservabilityProvider` lida com telemetria, o `A365ToolingClient` gerencia acesso a ferramentas MCP e o `OpenAIMcpRegistrationService` registra servidores MCP com o OpenAI Agents SDK.

---

## Resumo

| Conceito | Principal aprendizado |
|---------|-------------|
| **Agent 365 ≠ framework de agentes** | Ele adiciona *capacidades empresariais* sobre o seu agente existente — não substitui SK, LangChain, etc. |
| **Entra Agent ID** | Cada agente recebe sua própria identidade — como uma conta de usuário, mas para um agente |
| **Blueprint** | Modelo aprovado pelo TI; todas as instâncias herdam suas regras de governança |
| **Observabilidade** | Auto-instrumentação OpenTelemetry — cada chamada de ferramenta e inferência LLM é rastreada |
| **MCP Governado** | Ferramentas do M365 (Mail, Calendar, Teams, SharePoint) acessíveis sob controle do TI |
| **Notificações** | Agentes podem ser @mencionados no Teams, receber e-mails, responder a comentários no Word |
| **Frontier obrigatório** | Ainda em preview — requer licença M365 Copilot + inscrição no programa Frontier |

---

## Próximos Passos

- **Construa o agente subjacente primeiro:** → [Lab 016 — OpenAI Agents SDK](lab-016-openai-agents-sdk.md)
- **Adicione ferramentas MCP ao seu agente:** → [Lab 020 — MCP Server em Python](lab-020-mcp-server-python.md)
- **Aprofundamento em observabilidade:** → [Lab 033 — Observabilidade de Agentes com App Insights](lab-033-agent-observability.md)
- **Pipeline RAG empresarial:** → [Lab 042 — RAG Empresarial com Avaliações](lab-042-enterprise-rag.md)
