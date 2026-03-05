---
tags: [teams, javascript, free, github-models]
---
# Lab 024: Teams AI Library Bot

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Path:</strong> <a href="../paths/agent-builder-teams/">Agent Builder — Teams</a></span>
  <span><strong>Time:</strong> ~60 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Microsoft 365 Developer Program (free) + GitHub Models</span>
</div>

!!! info "Traduction en cours"
    Ce lab est en cours de traduction. Le contenu ci-dessous est en anglais.



## What You'll Learn

- Build a **code-first Teams bot** with the Teams AI Library (JavaScript)
- Connect the bot to **GitHub Models** (no Azure OpenAI needed)
- Run locally with the **Teams Toolkit** and Teams App Test Tool
- Handle user messages, adaptive cards, and actions
- Add AI-powered responses using the AI module

---

## Introduction

The **Teams AI Library** is a JavaScript/TypeScript SDK for building AI-powered bots that run natively in Microsoft Teams. Unlike Copilot Studio (no-code), Teams AI Library gives you full programmatic control — custom logic, webhook integrations, complex state management.

This lab builds the OutdoorGear customer service bot for Teams.

---

## Prerequisites

- Node.js 18+ (`node --version`)
- **Teams Toolkit VS Code extension** (install from VS Code marketplace)
- **Microsoft 365 Developer Program** tenant (free at [developer.microsoft.com/microsoft-365/dev-program](https://developer.microsoft.com/microsoft-365/dev-program))
- `GITHUB_TOKEN` set

!!! tip "Free M365 Developer tenant"
    The M365 Developer Program gives you a free 90-day sandbox tenant with Teams, SharePoint, and all Microsoft 365 apps — renewable if active.

---

## Lab Exercise

### Step 1: Create the project

```bash
# Install Teams Toolkit CLI
npm install -g @microsoft/teamsapp-cli

# Create a new bot project
teamsapp new

# Select: Bot → AI Bot → JavaScript → Teams AI Library
```

Or use VS Code:
1. Open VS Code → Teams Toolkit extension (left sidebar)
2. Click **Create a New App** → **Bot** → **AI Bot** → **JavaScript**
3. Name: `OutdoorGearBot`

### Step 2: Project structure

```
OutdoorGearBot/
├── src/
│   ├── app.js          ← Bot application entry point
│   ├── config.js       ← Configuration (model, storage)
│   └── prompts/
│       └── chat/
│           ├── skprompt.txt    ← System prompt
│           └── config.json     ← Model parameters
├── appPackage/
│   ├── manifest.json   ← Teams app manifest
│   └── ...
└── teamsapp.yml        ← Teams Toolkit config
```

### Step 3: Configure GitHub Models

Edit `src/config.js`:

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

Edit `src/app.js`:

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

### Step 4: Write the system prompt

Edit `src/prompts/chat/skprompt.txt`:

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

Edit `src/prompts/chat/config.json`:

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

### Step 5: Run locally with Teams App Test Tool

```bash
npm install
teamsapp preview --env local
```

This opens the **Teams App Test Tool** — a browser-based simulator that lets you test your bot without deploying to real Teams.

Try:
- `What boots do you have?`
- `Tell me about your return policy`
- `I need a tent for 2 people in winter`
- `/reset`

### Step 6: Add an Adaptive Card response

Adaptive Cards make bot responses rich and interactive:

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

## Architecture

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

## Next Steps

- **No-code Teams agent:** → [Lab 011 — Copilot Studio](lab-011-copilot-studio-first-agent.md)
- **Deploy to Azure:** → [Lab 028 — Deploy to Container Apps](lab-028-deploy-mcp-azure.md)
