---
tags: [vscode, typescript, github-copilot, free]
---
# Lab 025 : Participant de chat VS Code Copilot

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/agent-builder-vscode/">Agent Builder — VS Code</a></span>
  <span><strong>Durée :</strong> ~45 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Abonnement GitHub Copilot OU API Language Model VS Code (gratuit dans VS Code)</span>
</div>

## Ce que vous apprendrez

- Comment les **participants de chat** VS Code étendent GitHub Copilot Chat
- Créer un participant personnalisé `@outdoorgear` qui répond aux questions sur les produits
- Utiliser l'**API Language Model de VS Code** — aucune clé API externe nécessaire
- Gérer les **commandes slash** (`/search`, `/policy`)
- Diffuser les réponses en temps réel

---

## Introduction

Les participants de chat VS Code sont des agents personnalisés qui se branchent directement dans GitHub Copilot Chat avec le préfixe `@`. Quand un utilisateur tape `@outdoorgear what tents do you have?`, votre extension gère la requête.

L'**API Language Model** (`vscode.lm`) donne aux extensions accès au même LLM qui alimente Copilot — gratuitement, en utilisant l'abonnement GitHub Copilot existant de l'utilisateur.

---

## Prérequis

- VS Code 1.90+
- Abonnement GitHub Copilot (essai gratuit disponible)
- Node.js 18+
- `npm install -g yo generator-code`

---

## Exercice du lab

### Étape 1 : Scaffolder une extension VS Code

```bash
mkdir outdoorgear-participant && cd outdoorgear-participant
npx --yes yo code
```

Sélectionnez :
- **New Extension (TypeScript)**
- Nom : `outdoorgear-participant`
- Identifiant : `outdoorgear-participant`
- Description : `OutdoorGear product assistant for Copilot Chat`
- Bundler webpack : **Non**

Ouvrez dans VS Code :
```bash
code .
```

### Étape 2 : Installer les définitions de types

```bash
npm install --save-dev @types/vscode
```

Mettez à jour `package.json` — définissez la version du moteur et ajoutez la contribution du participant de chat :

```json
{
  "engines": { "vscode": "^1.90.0" },
  "contributes": {
    "chatParticipants": [
      {
        "id": "outdoorgear.assistant",
        "fullName": "OutdoorGear Assistant",
        "name": "outdoorgear",
        "description": "Ask about outdoor gear products, policies, and recommendations.",
        "isSticky": true,
        "commands": [
          {
            "name": "search",
            "description": "Search products by keyword"
          },
          {
            "name": "policy",
            "description": "Ask about return, shipping, or warranty policies"
          }
        ]
      }
    ]
  }
}
```

### Étape 3 : Écrire le gestionnaire du participant

Remplacez `src/extension.ts` par :

```typescript
import * as vscode from 'vscode';

// Sample product data (in production, load from API/MCP server)
const PRODUCTS = [
    { name: 'TrailBlazer X200', category: 'footwear', price: 189.99, description: 'Waterproof Gore-Tex hiking boot. Vibram outsole, 3-season rated.' },
    { name: 'Summit Pro Tent',   category: 'camping',  price: 349.00, description: '2-person 4-season tent. DAC aluminum poles, 2.1kg.' },
    { name: 'ClimbTech Pro Harness', category: 'climbing', price: 129.99, description: 'CE EN12277 certified. 15kN rated. Dyneema blend.' },
    { name: 'OmniPack 45L',     category: 'packs',    price: 279.99, description: 'Technical 45L pack with hip belt, hydration sleeve.' },
    { name: 'StormShell Jacket', category: 'clothing', price: 349.00, description: '3-layer Gore-Tex Pro shell. 20k/20k waterproof.' },
];

const POLICIES: Record<string, string> = {
    return:   '60-day return window. Items must be unused in original packaging. Worn footwear non-refundable unless defective.',
    shipping: 'Standard $5.99 (3-5 days). Express $14.99 (1-2 days). Free on orders $75+. Same-day in Seattle, Portland, Denver.',
    warranty: '2-year warranty on all products. Lifetime warranty on climbing/safety gear. Proof of purchase required.',
};

function searchProducts(query: string): string {
    const q = query.toLowerCase();
    const matches = PRODUCTS.filter(p =>
        p.name.toLowerCase().includes(q) ||
        p.category.toLowerCase().includes(q) ||
        p.description.toLowerCase().includes(q)
    );
    if (matches.length === 0) { return 'No products found for that query.'; }
    return matches.map(p =>
        `**${p.name}** — $${p.price}\n${p.description} _(${p.category})_`
    ).join('\n\n');
}

export function activate(context: vscode.ExtensionContext) {
    const handler: vscode.ChatRequestHandler = async (
        request: vscode.ChatRequest,
        context: vscode.ChatContext,
        stream: vscode.ChatResponseStream,
        token: vscode.CancellationToken
    ) => {
        // Handle slash commands
        if (request.command === 'search') {
            const results = searchProducts(request.prompt);
            stream.markdown(results);
            return;
        }

        if (request.command === 'policy') {
            const prompt = request.prompt.toLowerCase();
            const key = Object.keys(POLICIES).find(k => prompt.includes(k));
            if (key) {
                stream.markdown(`**${key.charAt(0).toUpperCase() + key.slice(1)} Policy:**\n\n${POLICIES[key]}`);
            } else {
                stream.markdown(`Available policies: **return**, **shipping**, **warranty**\n\nTry: \`@outdoorgear /policy return\``);
            }
            return;
        }

        // General question — use the Language Model API
        const productContext = PRODUCTS.map(p =>
            `- ${p.name} ($${p.price}): ${p.description}`
        ).join('\n');

        const policyContext = Object.entries(POLICIES)
            .map(([k, v]) => `${k}: ${v}`)
            .join('\n');

        const systemPrompt = `You are a helpful outdoor gear shopping assistant for OutdoorGear Inc.
Answer questions using ONLY the provided product and policy context.
Be concise and friendly.

PRODUCTS:
${productContext}

POLICIES:
${policyContext}`;

        // Select the best available model (Copilot)
        const models = await vscode.lm.selectChatModels({
            vendor: 'copilot',
            family: 'gpt-4o-mini'
        });

        if (models.length === 0) {
            stream.markdown('⚠️ No language model available. Make sure GitHub Copilot is installed and signed in.');
            return;
        }

        const model = models[0];

        const messages = [
            vscode.LanguageModelChatMessage.User(systemPrompt),
            vscode.LanguageModelChatMessage.User(request.prompt),
        ];

        const response = await model.sendRequest(messages, {}, token);

        // Stream the response token by token
        for await (const chunk of response.text) {
            stream.markdown(chunk);
        }
    };

    // Register the participant
    const participant = vscode.chat.createChatParticipant(
        'outdoorgear.assistant',
        handler
    );

    // Add a welcome message
    participant.welcomeMessageProvider = {
        provideWelcomeMessage: async () => {
            return {
                icon: new vscode.ThemeIcon('outdoor-gear'),
                message: new vscode.MarkdownString(
                    '👋 Hi! I\'m the **OutdoorGear Assistant**.\n\n' +
                    'I can help you with:\n' +
                    '- `@outdoorgear /search hiking boots` — Find products\n' +
                    '- `@outdoorgear /policy return` — Policy questions\n' +
                    '- `@outdoorgear What tent is best for winter?` — General questions'
                )
            };
        }
    };

    context.subscriptions.push(participant);
}

export function deactivate() {}
```

### Étape 4 : Exécuter et tester l'extension

Appuyez sur **F5** pour ouvrir un hôte de développement d'extension (une nouvelle fenêtre VS Code).

Dans la nouvelle fenêtre, ouvrez Copilot Chat et essayez :

```
@outdoorgear What waterproof boots do you have?
@outdoorgear /search climbing
@outdoorgear /policy return
@outdoorgear I'm hiking Rainier in January, what do I need?
```

### Étape 5 : Ajouter des suggestions de suivi

Améliorez l'expérience utilisateur en suggérant des questions de suivi :

```typescript
// Add inside the handler, before the return at end of general question block:
stream.button({
    command: 'workbench.action.chat.open',
    title: '🔍 Search all products',
    arguments: ['@outdoorgear /search ']
});

// Suggested follow-ups
return {
    followUp: [
        { prompt: '/policy return', label: '📦 Return policy', command: 'policy' },
        { prompt: '/policy shipping', label: '🚚 Shipping info', command: 'policy' },
    ]
};
```

---

## Fonctionnement de l'API Language Model

```
L'utilisateur tape : @outdoorgear What tent for winter?
       │
       ▼
VS Code route vers le gestionnaire de votre participant
       │
       ▼
Votre code : construit le contexte + le prompt
       │
       ▼
vscode.lm.selectChatModels() → utilise le modèle de Copilot
       │
       ▼
model.sendRequest() → diffuse les tokens en retour
       │
       ▼
stream.markdown() → rendu dans le panneau Chat
```

Pas de clé API externe. Pas de coût réseau. Utilise l'abonnement Copilot de l'utilisateur.

---

## Publication (optionnel)

```bash
npm install -g @vscode/vsce
vsce package
# Creates outdoorgear-participant-1.0.0.vsix

# Install locally for testing
code --install-extension outdoorgear-participant-1.0.0.vsix

# Publish to marketplace (requires publisher account at marketplace.visualstudio.com)
vsce publish
```

---

## Prochaines étapes

- **Construire une extension Copilot complète (GitHub.com) :** → [Lab 041 — Extension GitHub Copilot personnalisée](lab-041-copilot-extension.md)
- **Connecter votre participant à un serveur MCP :** → [Lab 020 — Serveur MCP en Python](lab-020-mcp-server-python.md)
