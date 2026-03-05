---
tags: [vscode, typescript, github-copilot, free]
---
# Lab 025: VS Code Copilot Chat Participant

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Path:</strong> <a href="../paths/agent-builder-vscode/">Agent Builder — VS Code</a></span>
  <span><strong>Time:</strong> ~45 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — GitHub Copilot subscription OR VS Code Language Model API (free in VS Code)</span>
</div>

!!! info "Traduction en cours"
    Ce lab est en cours de traduction. Le contenu ci-dessous est en anglais.



## What You'll Learn

- How VS Code **Chat Participants** extend GitHub Copilot Chat
- Create a custom `@outdoorgear` participant that answers product questions
- Use the **VS Code Language Model API** — no external API keys needed
- Handle **slash commands** (`/search`, `/policy`)
- Stream responses in real-time

---

## Introduction

VS Code Chat Participants are custom agents that plug directly into GitHub Copilot Chat using the `@` prefix. When a user types `@outdoorgear what tents do you have?`, your extension handles the request.

The **Language Model API** (`vscode.lm`) gives extensions access to the same LLM powering Copilot — for free, using the user's existing GitHub Copilot subscription.

---

## Prerequisites

- VS Code 1.90+
- GitHub Copilot subscription (free trial available)
- Node.js 18+
- `npm install -g yo generator-code`

---

## Lab Exercise

### Step 1: Scaffold a VS Code extension

```bash
mkdir outdoorgear-participant && cd outdoorgear-participant
npx --yes yo code
```

Select:
- **New Extension (TypeScript)**
- Name: `outdoorgear-participant`
- Identifier: `outdoorgear-participant`
- Description: `OutdoorGear product assistant for Copilot Chat`
- Bundle with webpack: **No**

Open in VS Code:
```bash
code .
```

### Step 2: Install type definitions

```bash
npm install --save-dev @types/vscode
```

Update `package.json` — set the engine version and add chat participant contribution:

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

### Step 3: Write the participant handler

Replace `src/extension.ts` with:

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

### Step 4: Run and test the extension

Press **F5** to open an Extension Development Host (a new VS Code window).

In the new window, open Copilot Chat and try:

```
@outdoorgear What waterproof boots do you have?
@outdoorgear /search climbing
@outdoorgear /policy return
@outdoorgear I'm hiking Rainier in January, what do I need?
```

### Step 5: Add follow-up suggestions

Improve UX by suggesting follow-up questions:

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

## How the Language Model API Works

```
User types: @outdoorgear What tent for winter?
       │
       ▼
VS Code routes to your participant handler
       │
       ▼
Your code: build context + prompt
       │
       ▼
vscode.lm.selectChatModels() → uses Copilot's model
       │
       ▼
model.sendRequest() → streams tokens back
       │
       ▼
stream.markdown() → renders in Chat panel
```

No external API key. No network cost. Uses the user's Copilot subscription.

---

## Publishing (Optional)

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

## Next Steps

- **Build a full Copilot Extension (GitHub.com):** → [Lab 041 — Custom GitHub Copilot Extension](lab-041-copilot-extension.md)
- **Connect your participant to an MCP server:** → [Lab 020 — MCP Server in Python](lab-020-mcp-server-python.md)
