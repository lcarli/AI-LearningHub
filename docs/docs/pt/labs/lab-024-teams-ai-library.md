---
tags: [teams, javascript, free, github-models]
---
# Lab 024: Bot com Teams AI Library

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/agent-builder-teams/">Agent Builder — Teams</a></span>
  <span><strong>Tempo:</strong> ~60 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Microsoft 365 Developer Program (gratuito) + GitHub Models</span>
</div>

## O que Você Vai Aprender

- Construir um **bot de Teams code-first** com a Teams AI Library (JavaScript)
- Conectar o bot ao **GitHub Models** (sem necessidade de Azure OpenAI)
- Executar localmente com o **Teams Toolkit** e o Teams App Test Tool
- Lidar com mensagens de usuários, adaptive cards e ações
- Adicionar respostas com IA usando o módulo AI

---

## Introdução

A **Teams AI Library** é um SDK em JavaScript/TypeScript para construir bots com IA que rodam nativamente no Microsoft Teams. Diferente do Copilot Studio (sem código), a Teams AI Library oferece controle programático completo — lógica personalizada, integrações com webhooks, gerenciamento de estado complexo.

Este lab constrói o bot de atendimento ao cliente OutdoorGear para o Teams.

---

## Pré-requisitos

- Node.js 18+ (`node --version`)
- **Extensão Teams Toolkit para VS Code** (instale pelo marketplace do VS Code)
- **Tenant do Microsoft 365 Developer Program** (gratuito em [developer.microsoft.com/microsoft-365/dev-program](https://developer.microsoft.com/microsoft-365/dev-program))
- `GITHUB_TOKEN` configurado

!!! tip "Tenant M365 Developer gratuito"
    O M365 Developer Program oferece um tenant sandbox gratuito de 90 dias com Teams, SharePoint e todos os apps do Microsoft 365 — renovável se ativo.

---

## Exercício do Lab

### Passo 1: Criar o projeto

```bash
# Install Teams Toolkit CLI
npm install -g @microsoft/teamsapp-cli

# Create a new bot project
teamsapp new

# Select: Bot → AI Bot → JavaScript → Teams AI Library
```

Ou use o VS Code:
1. Abra o VS Code → extensão Teams Toolkit (barra lateral esquerda)
2. Clique em **Create a New App** → **Bot** → **AI Bot** → **JavaScript**
3. Nome: `OutdoorGearBot`

### Passo 2: Estrutura do projeto

```
OutdoorGearBot/
├── src/
│   ├── app.js          ← Ponto de entrada da aplicação do bot
│   ├── config.js       ← Configuração (modelo, armazenamento)
│   └── prompts/
│       └── chat/
│           ├── skprompt.txt    ← Prompt do sistema
│           └── config.json     ← Parâmetros do modelo
├── appPackage/
│   ├── manifest.json   ← Manifesto do app Teams
│   └── ...
└── teamsapp.yml        ← Configuração do Teams Toolkit
```

### Passo 3: Configurar o GitHub Models

Edite `src/config.js`:

```javascript
const config = {
    botId: process.env.BOT_ID,
    botPassword: process.env.BOT_PASSWORD,

    // Use GitHub Models (OpenAI-compatible, free)
    openAIKey: process.env.GITHUB_TOKEN,
    openAIEndpoint: "https://models.inference.ai.azure.com",
    openAIModel: "gpt-4o-mini",
};

module.exports = config;
```

Edite `src/app.js`:

```javascript
const { Application, AI, preview } = require("@microsoft/teams-ai");
const { OpenAIModel, PromptManager, ActionPlanner } = preview;
const config = require("./config");
const path = require("path");

// Create OpenAI model pointing to GitHub Models
const model = new OpenAIModel({
    apiKey: config.openAIKey,
    endpoint: config.openAIEndpoint,
    defaultModel: config.openAIModel,
    useSystemPrompt: true,
    logRequests: true,
});

const prompts = new PromptManager({
    promptsFolder: path.join(__dirname, "prompts"),
});

const planner = new ActionPlanner({
    model,
    prompts,
    defaultPrompt: "chat",
});

const app = new Application({
    storage: new MemoryStorage(),
    ai: { planner },
});

// Handle messages
app.message("/reset", async (context, state) => {
    state.deleteConversationState();
    await context.sendActivity("Conversation reset! How can I help you?");
});

// Default: handled by AI planner
module.exports = { app };
```

### Passo 4: Escrever o prompt do sistema

Edite `src/prompts/chat/skprompt.txt`:

```
You are OutdoorGear Assistant — a friendly customer service bot for OutdoorGear Inc.

You help customers with:
- Product questions (boots, tents, packs, jackets, climbing gear)
- Order status and tracking
- Return policy (60-day window, unused items, not worn footwear)
- Shipping info ($5.99 standard 3-5 days, free over $75)
- Warranty claims (2-year standard, lifetime on climbing gear)

Key products:
- TrailBlazer X200 hiking boot — $189.99, Gore-Tex waterproof, Vibram outsole
- Summit Pro Tent — $349, 2-person 4-season, DAC aluminum poles
- OmniPack 45L pack — $279.99, technical backpack with hip belt
- StormShell Jacket — $349, 3-layer Gore-Tex Pro, 20k/20k waterproof
- ClimbTech Pro Harness — $129.99, CE EN12277, 15kN rated

Be friendly, concise, and always recommend visiting outdoorgear.com for purchases.
For order tracking, ask for the order number and direct to outdoorgear.com/orders.

Conversation history:
{{$conversation}}
```

Edite `src/prompts/chat/config.json`:

```json
{
  "schema": 1.1,
  "description": "OutdoorGear customer service chat",
  "type": "completion",
  "completion": {
    "model": "gpt-4o-mini",
    "completion_type": "chat",
    "include_history": true,
    "include_input": true,
    "max_input_tokens": 2800,
    "max_tokens": 1000,
    "temperature": 0.7
  }
}
```

### Passo 5: Executar localmente com o Teams App Test Tool

```bash
npm install
teamsapp preview --env local
```

Isso abre o **Teams App Test Tool** — um simulador baseado em navegador que permite testar seu bot sem implantá-lo no Teams real.

Experimente:
- `What boots do you have?`
- `Tell me about your return policy`
- `I need a tent for 2 people in winter`
- `/reset`

### Passo 6: Adicionar uma resposta com Adaptive Card

Adaptive Cards tornam as respostas do bot ricas e interativas:

```javascript
// In app.js — add after planner setup:
app.message("show products", async (context, state) => {
    await context.sendActivity({
        attachments: [{
            contentType: "application/vnd.microsoft.card.adaptive",
            content: {
                type: "AdaptiveCard",
                version: "1.5",
                body: [
                    { type: "TextBlock", text: "🏔️ OutdoorGear Products", size: "Large", weight: "Bolder" },
                    { type: "FactSet", facts: [
                        { title: "TrailBlazer X200", value: "$189.99 — Waterproof hiking boot" },
                        { title: "Summit Pro Tent",   value: "$349.00 — 4-season, 2-person" },
                        { title: "OmniPack 45L",     value: "$279.99 — Technical backpack" },
                        { title: "StormShell Jacket", value: "$349.00 — Gore-Tex Pro shell" },
                    ]},
                ],
                actions: [
                    { type: "Action.OpenUrl", title: "Shop Now", url: "https://outdoorgear.com" },
                ]
            }
        }]
    });
});
```

---

## Arquitetura

```
Teams Client
    │  (Bot Framework)
    ▼
Bot Framework Adapter
    │
    ▼
Teams AI Library Application
    ├── Message router (custom handlers)
    ├── AI Planner → OpenAI/GitHub Models
    │       └── PromptManager (skprompt.txt)
    └── Adaptive Card renderer
```

---

## Próximos Passos

- **Agente Teams sem código:** → [Lab 011 — Copilot Studio](lab-011-copilot-studio-first-agent.md)
- **Implantar no Azure:** → [Lab 028 — Implantar no Container Apps](lab-028-deploy-mcp-azure.md)
