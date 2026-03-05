---
tags: [a2a, protocol, multi-agent, interoperability, python, free]
---
# Lab 054: Protocolo A2A — Construa Sistemas Multi-Agente Interoperáveis

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Trilha:</strong> Todas as trilhas</span>
  <span><strong>Tempo:</strong> ~75 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Usa apenas dados JSON locais</span>
</div>

!!! tip "Os Três Protocolos Agênticos"
    A2A é um dos três protocolos abertos para a era agêntica: **MCP** (agente↔ferramentas, [Lab 012](lab-012-what-is-mcp.md)), **A2A** (agente↔agente, este lab), e **AG-UI** (agente↔usuário, [Lab 077](lab-077-agui-protocol.md)). Juntos, eles formam a pilha completa de interoperabilidade.

## O Que Você Vai Aprender

- O que é o **protocolo A2A (Agent-to-Agent)** — JSON-RPC 2.0 sobre HTTPS, governado pela Linux Foundation
- Como os **Agent Cards** funcionam como mecanismo de descoberta de capacidades dos agentes
- Como analisar programaticamente Agent Cards e inspecionar **skills**, **streaming** e **pushNotifications**
- As principais diferenças entre **A2A** (comunicação peer-to-peer entre agentes) e **MCP** (acesso de agente a ferramenta)

## Introdução

Sistemas modernos de IA raramente consistem em um único agente. Soluções do mundo real requerem **múltiplos agentes especializados** que se descobrem mutuamente, negociam capacidades e colaboram em tarefas. O **protocolo Agent-to-Agent (A2A)** padroniza essa comunicação.

A2A e MCP resolvem problemas diferentes:

| Protocolo | Propósito | Direção |
|-----------|-----------|---------|
| **A2A** | Comunicação Agente ↔ Agente | Peer-to-peer — agentes delegam tarefas a outros agentes |
| **MCP** | Acesso Agente → Ferramenta | Cliente-servidor — agentes chamam ferramentas, bancos de dados, APIs |

Pense em A2A como agentes *conversando entre si*, e MCP como agentes *usando ferramentas*. Um sistema multi-agente completo tipicamente usa **ambos** os protocolos.

### O Cenário

Você é um **Arquiteto de Integração** na OutdoorGear Inc. A empresa opera **3 agentes especializados**:

1. **ProductSearchAgent** — pesquisa o catálogo de produtos por categoria, preço e disponibilidade
2. **OrderManagementAgent** — gerencia pedidos, devoluções e atualizações de envio
3. **CustomerSupportAgent** — lida com consultas, reclamações e respostas de FAQ

Cada agente publica um **Agent Card** — um documento JSON descrevendo sua identidade, capacidades, habilidades e requisitos de autenticação. Seu trabalho é carregar esses cards, analisar o que cada agente pode fazer e entender como o A2A permite que eles se descubram e colaborem entre si.

!!! info "Fundamentos do Protocolo A2A"
    O A2A usa **JSON-RPC 2.0 sobre HTTPS** como camada de transporte. Cada agente publica um Agent Card em uma URL conhecida (tipicamente `/.well-known/agent.json`). Agentes clientes descobrem agentes disponíveis buscando esses cards, inspecionando suas habilidades e enviando requisições de tarefas usando o protocolo JSON-RPC.

## Pré-requisitos

| Requisito | Motivo |
|---|---|
| Python 3.10+ | Analisar e processar Agent Cards |
| `json` (built-in) | Carregar dados do agent card |

Nenhum pacote externo é necessário — este lab usa apenas a biblioteca padrão do Python.

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-054/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `agent_cards.json` | Arquivo de configuração / dados | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-054/agent_cards.json) |
| `broken_a2a.py` | Exercício de correção de bugs (3 bugs + auto-testes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-054/broken_a2a.py) |

---

## Etapa 1: Entendendo o Protocolo A2A

O A2A define um padrão para **comunicação peer-to-peer entre agentes**. O protocolo especifica:

| Conceito | Descrição |
|----------|-----------|
| **Agent Card** | Documento JSON que anuncia a identidade, URL, capacidades, habilidades e autenticação de um agente |
| **Skills** | Operações nomeadas que um agente pode realizar (ex.: `search_products`, `track_order`) |
| **Capabilities** | Flags de funcionalidade: `streaming`, `pushNotifications`, `stateTransitionHistory` |
| **Task** | Uma unidade de trabalho enviada de um agente para outro via JSON-RPC 2.0 |
| **Artifact** | O resultado retornado por um agente após completar uma tarefa |

### Estrutura do Agent Card

```json
{
  "name": "ProductSearchAgent",
  "description": "Searches the OutdoorGear product catalog",
  "url": "https://agents.outdoorgear.com/product-search",
  "version": "1.0.0",
  "provider": "OutdoorGear Inc.",
  "capabilities": {
    "streaming": true,
    "pushNotifications": false,
    "stateTransitionHistory": false
  },
  "skills": [
    {"id": "search_products", "name": "Search Products", "description": "Search by category, price, and stock"}
  ],
  "authentication": {"type": "bearer", "required": true}
}
```

### Fluxo de Comunicação A2A

```
┌─────────────┐   1. Fetch Agent Card    ┌─────────────────┐
│  Client     │ ───────────────────────►  │  Remote Agent   │
│  Agent      │   2. Inspect skills      │  (Agent Card)   │
│             │ ◄───────────────────────  │                 │
│             │   3. Send JSON-RPC task   │                 │
│             │ ───────────────────────►  │                 │
│             │   4. Receive artifact     │                 │
│             │ ◄───────────────────────  │                 │
└─────────────┘                           └─────────────────┘
```

---

## Etapa 2: Carregar Agent Cards

Carregue os três agent cards da OutdoorGear a partir do arquivo JSON:

```python
import json

with open("lab-054/agent_cards.json") as f:
    cards = json.load(f)

print(f"Total agents: {len(cards)}")
for card in cards:
    print(f"  • {card['name']} (v{card['version']}) — {card['description']}")
```

**Saída esperada:**

```
Total agents: 3
  • ProductSearchAgent (v1.0.0) — Searches the OutdoorGear product catalog by category, price range, and availability
  • OrderManagementAgent (v2.1.0) — Manages customer orders including status tracking, returns, and shipping updates
  • CustomerSupportAgent (v1.3.0) — Handles customer inquiries, complaints, and FAQ responses with sentiment awareness
```

---

## Etapa 3: Analisar Capacidades dos Agentes

Analise as capacidades, habilidades e autenticação de cada agente para construir um resumo de descoberta:

### 3a — Inventário de Habilidades

```python
total_skills = 0
for card in cards:
    skills = card["skills"]
    total_skills += len(skills)
    print(f"\n{card['name']} — {len(skills)} skill(s):")
    for skill in skills:
        print(f"  • {skill['name']}: {skill['description']}")

print(f"\nTotal skills across all agents: {total_skills}")
```

**Saída esperada:**

```
ProductSearchAgent — 2 skill(s):
  • Search Products: Search by category, price, and stock
  • Get Product Details: Retrieve full specs for a product ID

OrderManagementAgent — 3 skill(s):
  • Track Order: Get real-time order status
  • Process Return: Initiate a product return
  • Update Shipping: Change shipping address or speed

CustomerSupportAgent — 2 skill(s):
  • Answer FAQ: Respond to common questions
  • Handle Complaint: Process and resolve complaints

Total skills across all agents: 7
```

### 3b — Flags de Capacidade

```python
print("Agent Capabilities Matrix:")
print(f"{'Agent':<25} {'Streaming':<12} {'Push':<12} {'History':<12}")
print("-" * 61)
for card in cards:
    caps = card["capabilities"]
    print(f"{card['name']:<25} {str(caps['streaming']):<12} "
          f"{str(caps['pushNotifications']):<12} "
          f"{str(caps['stateTransitionHistory']):<12}")

push_count = sum(1 for c in cards if c["capabilities"]["pushNotifications"])
print(f"\nAgents supporting pushNotifications: {push_count}")
```

**Saída esperada:**

```
Agent Capabilities Matrix:
Agent                     Streaming    Push         History
-------------------------------------------------------------
ProductSearchAgent        True         False        False
OrderManagementAgent      False        True         True
CustomerSupportAgent      True         True         False

Agents supporting pushNotifications: 2
```

### 3c — Tipos de Autenticação

```python
auth_types = sorted(set(c["authentication"]["type"] for c in cards))
print(f"Authentication types used: {auth_types}")

for card in cards:
    auth = card["authentication"]
    print(f"  {card['name']}: {auth['type']} (required={auth['required']})")
```

**Saída esperada:**

```
Authentication types used: ['bearer', 'oauth2']
  ProductSearchAgent: bearer (required=True)
  OrderManagementAgent: bearer (required=True)
  CustomerSupportAgent: oauth2 (required=True)
```

---

## Etapa 4: A2A vs MCP — Comparação de Protocolos

Entender quando usar cada protocolo é essencial para arquitetura multi-agente:

| Dimensão | A2A | MCP |
|----------|-----|-----|
| **Propósito** | Delegação de tarefas agente-para-agente | Acesso agente-para-ferramenta |
| **Transporte** | JSON-RPC 2.0 sobre HTTPS | JSON-RPC 2.0 sobre stdio/SSE |
| **Descoberta** | Agent Cards em `/.well-known/agent.json` | Manifestos de ferramentas no servidor MCP |
| **Direção** | Peer-to-peer (bidirecional) | Cliente → Servidor (unidirecional) |
| **Autenticação** | OAuth 2.0, bearer tokens | Definida pelo servidor (API keys, OAuth) |
| **Governança** | Linux Foundation | Anthropic (padrão aberto) |
| **Caso de uso** | "Peça a outro agente para fazer algo" | "Chame uma ferramenta / leia um recurso" |

### Quando Usar Qual

```
Customer asks: "Find me a waterproof tent under $200 and track my last order"

                    ┌──────────────────┐
                    │  Coordinator     │
                    │  Agent           │
                    └──────┬───────────┘
                           │
              ┌────────────┼────────────┐
         A2A  │       A2A  │            │ A2A
              ▼            ▼            ▼
    ┌──────────────┐ ┌──────────┐ ┌──────────────┐
    │ ProductSearch │ │ Order    │ │ Customer     │
    │ Agent        │ │ Mgmt     │ │ Support      │
    └──────┬───────┘ └────┬─────┘ └──────┬───────┘
      MCP  │         MCP  │         MCP  │
           ▼              ▼              ▼
    ┌──────────────┐ ┌──────────┐ ┌──────────────┐
    │ Catalog DB   │ │ Order DB │ │ FAQ KB       │
    │ (MCP Server) │ │ (MCP)    │ │ (MCP Server) │
    └──────────────┘ └──────────┘ └──────────────┘
```

- **A2A** conecta o Coordenador aos agentes especializados (delegação peer-to-peer)
- **MCP** conecta cada agente às suas ferramentas e fontes de dados de back-end

---

## Etapa 5: Construir um Fluxo Simulado de Requisição/Resposta A2A

Simule como um agente cliente descobre e se comunica com um agente remoto usando A2A:

```python
import json

def discover_agent(cards, skill_id):
    """Find an agent that has the requested skill."""
    for card in cards:
        for skill in card["skills"]:
            if skill["id"] == skill_id:
                return card
    return None

def build_a2a_request(card, skill_id, params):
    """Build a JSON-RPC 2.0 request for an A2A task."""
    return {
        "jsonrpc": "2.0",
        "method": "tasks/send",
        "id": "req-001",
        "params": {
            "id": "task-001",
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": json.dumps(params)}]
            },
            "metadata": {
                "target_agent": card["name"],
                "skill": skill_id
            }
        }
    }

def mock_a2a_response(request):
    """Simulate an A2A response."""
    return {
        "jsonrpc": "2.0",
        "id": request["id"],
        "result": {
            "id": request["params"]["id"],
            "status": {"state": "completed"},
            "artifacts": [
                {
                    "parts": [{"type": "text", "text": "Found 3 matching products"}]
                }
            ]
        }
    }

# Discovery: find who can search products
agent = discover_agent(cards, "search_products")
print(f"Discovered agent: {agent['name']} at {agent['url']}")

# Build request
request = build_a2a_request(agent, "search_products", {"category": "tents", "max_price": 200})
print(f"\nA2A Request:\n{json.dumps(request, indent=2)}")

# Get response
response = mock_a2a_response(request)
print(f"\nA2A Response:\n{json.dumps(response, indent=2)}")
```

**Saída esperada:**

```
Discovered agent: ProductSearchAgent at https://agents.outdoorgear.com/product-search

A2A Request:
{
  "jsonrpc": "2.0",
  "method": "tasks/send",
  "id": "req-001",
  "params": {
    "id": "task-001",
    "message": {
      "role": "user",
      "parts": [{"type": "text", "text": "{\"category\": \"tents\", \"max_price\": 200}"}]
    },
    "metadata": {
      "target_agent": "ProductSearchAgent",
      "skill": "search_products"
    }
  }
}

A2A Response:
{
  "jsonrpc": "2.0",
  "id": "req-001",
  "result": {
    "id": "task-001",
    "status": {"state": "completed"},
    "artifacts": [
      {
        "parts": [{"type": "text", "text": "Found 3 matching products"}]
      }
    ]
  }
}
```

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-054/broken_a2a.py` possui **3 bugs** no parser de Agent Card. Você consegue encontrar e corrigir todos?

Execute os auto-testes para ver quais falham:

```bash
python lab-054/broken_a2a.py
```

Você deve ver **3 testes falhando**. Cada teste corresponde a um bug:

| Teste | O que verifica | Dica |
|-------|---------------|------|
| Teste 1 | Contagem total de habilidades em todos os agentes | Deve somar as habilidades de *todos* os cards, não apenas do primeiro |
| Teste 2 | Agentes que suportam push notifications | Verifique `pushNotifications`, não `streaming` |
| Teste 3 | Tipos de autenticação | Retorne o campo `type` (string), não o campo `required` (bool) |

Corrija todos os 3 bugs e execute novamente. Quando você ver `🎉 All 3 tests passed`, está pronto!

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Qual mecanismo de transporte o protocolo A2A utiliza?"

    - A) gRPC sobre HTTP/2
    - B) JSON-RPC 2.0 sobre HTTPS
    - C) GraphQL sobre WebSocket
    - D) REST sobre HTTP com OpenAPI

    ??? success "✅ Revelar Resposta"
        **Correto: B) JSON-RPC 2.0 sobre HTTPS**

        O protocolo A2A usa **JSON-RPC 2.0 sobre HTTPS** como camada de transporte. Isso fornece um formato padronizado de requisição/resposta com nomes de métodos, parâmetros e códigos de erro — tudo transmitido de forma segura sobre HTTPS.

??? question "**Q2 (Múltipla Escolha):** Qual é o principal propósito de um Agent Card no A2A?"

    - A) Armazenar o histórico de conversas do agente
    - B) Descoberta de capacidades — anunciar o que um agente pode fazer
    - C) Criptografar mensagens entre agentes
    - D) Limitar a taxa de requisições recebidas

    ??? success "✅ Revelar Resposta"
        **Correto: B) Descoberta de capacidades — anunciar o que um agente pode fazer**

        Um Agent Card é um documento JSON publicado em uma URL conhecida que descreve a identidade, habilidades, capacidades (streaming, push notifications) e requisitos de autenticação de um agente. Agentes clientes buscam esses cards para **descobrir** o que agentes remotos podem fazer antes de enviar requisições de tarefas.

??? question "**Q3 (Execute o Lab):** Quantas habilidades no total existem nos 3 agentes da OutdoorGear?"

    Some os arrays de skills de todos os agent cards em [📥 `agent_cards.json`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-054/agent_cards.json).

    ??? success "✅ Revelar Resposta"
        **7**

        ProductSearchAgent tem 2 habilidades (`search_products`, `get_details`), OrderManagementAgent tem 3 habilidades (`track_order`, `process_return`, `update_shipping`), e CustomerSupportAgent tem 2 habilidades (`answer_faq`, `handle_complaint`). Total: 2 + 3 + 2 = **7**.

??? question "**Q4 (Execute o Lab):** Quantos agentes suportam `pushNotifications`?"

    Verifique o campo `capabilities.pushNotifications` em cada agent card.

    ??? success "✅ Revelar Resposta"
        **2**

        OrderManagementAgent (`pushNotifications: true`) e CustomerSupportAgent (`pushNotifications: true`) suportam push notifications. ProductSearchAgent não suporta (`pushNotifications: false`).

??? question "**Q5 (Execute o Lab):** Quais tipos de autenticação são usados nos 3 agentes?"

    Inspecione o campo `authentication.type` em cada card e colete os valores únicos.

    ??? success "✅ Revelar Resposta"
        **bearer e oauth2**

        ProductSearchAgent e OrderManagementAgent usam autenticação `bearer` token. CustomerSupportAgent usa `oauth2`. Os dois tipos únicos de autenticação são **bearer** e **oauth2**.

---

## Resumo

| Tópico | O Que Você Aprendeu |
|--------|---------------------|
| Protocolo A2A | JSON-RPC 2.0 sobre HTTPS para comunicação peer-to-peer entre agentes |
| Agent Cards | Documentos JSON para descoberta de capacidades (habilidades, capacidades, autenticação) |
| Habilidades & Capacidades | Como agentes anunciam o que podem fazer e quais funcionalidades suportam |
| A2A vs MCP | A2A para delegação agente↔agente; MCP para acesso agente→ferramenta |
| Fluxo de Descoberta | Buscar Agent Card → Inspecionar habilidades → Enviar tarefa → Receber artefato |

---

## Próximos Passos

- **[Lab 055](lab-055-a2a-mcp-capstone.md)** — A2A + MCP Full Stack — Capstone de Interoperabilidade de Agentes
- **[Lab 056](lab-056-federated-connectors.md)** — Conectores Federados M365 Copilot com MCP
