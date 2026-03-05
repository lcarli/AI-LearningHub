---
tags: [teams, javascript, free, github-models]
---
# Lab 024 : Bot Teams AI Library

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/agent-builder-teams/">Agent Builder — Teams</a></span>
  <span><strong>Durée :</strong> ~60 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Programme développeur Microsoft 365 (gratuit) + GitHub Models</span>
</div>

## Ce que vous apprendrez

- Construire un **bot Teams code-first** avec la Teams AI Library (JavaScript)
- Connecter le bot à **GitHub Models** (pas besoin d'Azure OpenAI)
- Exécuter localement avec le **Teams Toolkit** et l'outil de test Teams App
- Gérer les messages utilisateur, les cartes adaptatives et les actions
- Ajouter des réponses alimentées par l'IA via le module AI

---

## Introduction

La **Teams AI Library** est un SDK JavaScript/TypeScript pour construire des bots alimentés par l'IA qui fonctionnent nativement dans Microsoft Teams. Contrairement à Copilot Studio (no-code), la Teams AI Library vous donne un contrôle programmatique complet — logique personnalisée, intégrations webhook, gestion d'état complexe.

Ce lab construit le bot de service client OutdoorGear pour Teams.

---

## Prérequis

- Node.js 18+ (`node --version`)
- **Extension VS Code Teams Toolkit** (installer depuis le marketplace VS Code)
- **Locataire du Programme développeur Microsoft 365** (gratuit sur [developer.microsoft.com/microsoft-365/dev-program](https://developer.microsoft.com/microsoft-365/dev-program))
- `GITHUB_TOKEN` configuré

!!! tip "Locataire développeur M365 gratuit"
    Le Programme développeur M365 vous donne un locataire sandbox gratuit de 90 jours avec Teams, SharePoint et toutes les applications Microsoft 365 — renouvelable si actif.

---

## Exercice du lab

### Étape 1 : Créer le projet

```bash
# Install Teams Toolkit CLI
npm install -g @microsoft/teamsapp-cli

# Create a new bot project
teamsapp new

# Select: Bot → AI Bot → JavaScript → Teams AI Library
```

Ou utilisez VS Code :
1. Ouvrez VS Code → extension Teams Toolkit (barre latérale gauche)
2. Cliquez sur **Create a New App** → **Bot** → **AI Bot** → **JavaScript**
3. Nom : `OutdoorGearBot`

### Étape 2 : Structure du projet

```
OutdoorGearBot/
├── src/
│   ├── app.js          ← Point d'entrée de l'application bot
│   ├── config.js       ← Configuration (modèle, stockage)
│   └── prompts/
│       └── chat/
│           ├── skprompt.txt    ← Prompt système
│           └── config.json     ← Paramètres du modèle
├── appPackage/
│   ├── manifest.json   ← Manifeste de l'application Teams
│   └── ...
└── teamsapp.yml        ← Configuration Teams Toolkit
```

### Étape 3 : Configurer GitHub Models

Éditez `src/config.js` :

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

Éditez `src/app.js` :

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

### Étape 4 : Écrire le prompt système

Éditez `src/prompts/chat/skprompt.txt` :

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

Éditez `src/prompts/chat/config.json` :

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

### Étape 5 : Exécuter localement avec l'outil de test Teams App

```bash
npm install
teamsapp preview --env local
```

Cela ouvre l'**outil de test Teams App** — un simulateur dans le navigateur qui vous permet de tester votre bot sans le déployer dans le vrai Teams.

Essayez :
- `What boots do you have?`
- `Tell me about your return policy`
- `I need a tent for 2 people in winter`
- `/reset`

### Étape 6 : Ajouter une réponse par carte adaptative

Les cartes adaptatives rendent les réponses du bot riches et interactives :

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
    ├── Routeur de messages (gestionnaires personnalisés)
    ├── AI Planner → OpenAI/GitHub Models
    │       └── PromptManager (skprompt.txt)
    └── Moteur de rendu des cartes adaptatives
```

---

## Prochaines étapes

- **Agent Teams no-code :** → [Lab 011 — Copilot Studio](lab-011-copilot-studio-first-agent.md)
- **Déployer sur Azure :** → [Lab 028 — Déployer sur Container Apps](lab-028-deploy-mcp-azure.md)
