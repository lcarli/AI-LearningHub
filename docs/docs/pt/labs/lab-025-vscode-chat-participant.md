---
tags: [vscode, typescript, github-copilot, free]
---
# Lab 025: Participante do Chat do VS Code Copilot

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/agent-builder-vscode/">Agent Builder — VS Code</a></span>
  <span><strong>Tempo:</strong> ~45 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — assinatura do GitHub Copilot OU VS Code Language Model API (gratuita no VS Code)</span>
</div>

## O que Você Vai Aprender

- Como os **Chat Participants** do VS Code estendem o GitHub Copilot Chat
- Criar um participante personalizado `@outdoorgear` que responde perguntas sobre produtos
- Usar a **VS Code Language Model API** — sem necessidade de chaves de API externas
- Lidar com **slash commands** (`/search`, `/policy`)
- Transmitir respostas em tempo real

---

## Introdução

Chat Participants do VS Code são agentes personalizados que se conectam diretamente ao GitHub Copilot Chat usando o prefixo `@`. Quando um usuário digita `@outdoorgear what tents do you have?`, sua extensão lida com a solicitação.

A **Language Model API** (`vscode.lm`) dá às extensões acesso ao mesmo LLM que alimenta o Copilot — gratuitamente, usando a assinatura existente do GitHub Copilot do usuário.

---

## Pré-requisitos

- VS Code 1.90+
- Assinatura do GitHub Copilot (teste gratuito disponível)
- Node.js 18+
- `npm install -g yo generator-code`

---

## Exercício do Lab

### Passo 1: Criar a estrutura de uma extensão VS Code

```bash
mkdir outdoorgear-participant && cd outdoorgear-participant
npx --yes yo code
```

Selecione:
- **New Extension (TypeScript)**
- Nome: `outdoorgear-participant`
- Identificador: `outdoorgear-participant`
- Descrição: `OutdoorGear product assistant for Copilot Chat`
- Empacotar com webpack: **No**

Abra no VS Code:
```bash
code .
```

### Passo 2: Instalar as definições de tipos

```bash
npm install --save-dev @types/vscode
```

Atualize o `package.json` — defina a versão do engine e adicione a contribuição do chat participant:

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

### Passo 3: Escrever o handler do participante

Substitua `src/extension.ts` por:

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
        `**${p.name}** — $${p.price}
${p.description} _(${p.category})_`
    ).join('

');
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
                stream.markdown(`**${key.charAt(0).toUpperCase() + key.slice(1)} Policy:**

${POLICIES[key]}`);
            } else {
                stream.markdown(`Available policies: **return**, **shipping**, **warranty**

Try: \`@outdoorgear /policy return\``);
            }
            return;
        }

        // General question — use the Language Model API
        const productContext = PRODUCTS.map(p =>
            `- ${p.name} ($${p.price}): ${p.description}`
        ).join('
');

        const policyContext = Object.entries(POLICIES)
            .map(([k, v]) => `${k}: ${v}`)
            .join('
');

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
                    '👋 Hi! I'm the **OutdoorGear Assistant**.

' +
                    'I can help you with:
' +
                    '- `@outdoorgear /search hiking boots` — Find products
' +
                    '- `@outdoorgear /policy return` — Policy questions
' +
                    '- `@outdoorgear What tent is best for winter?` — General questions'
                )
            };
        }
    };

    context.subscriptions.push(participant);
}

export function deactivate() {}
```

### Passo 4: Executar e testar a extensão

Pressione **F5** para abrir um Extension Development Host (uma nova janela do VS Code).

Na nova janela, abra o Copilot Chat e experimente:

```
@outdoorgear What waterproof boots do you have?
@outdoorgear /search climbing
@outdoorgear /policy return
@outdoorgear I'm hiking Rainier in January, what do I need?
```

### Passo 5: Adicionar sugestões de acompanhamento

Melhore a experiência do usuário sugerindo perguntas de acompanhamento:

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

## Como a Language Model API Funciona

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

Sem chave de API externa. Sem custo de rede. Usa a assinatura Copilot do usuário.

---

## Publicação (Opcional)

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

## Próximos Passos

- **Construir uma Extensão Copilot completa (GitHub.com):** → [Lab 041 — Extensão Personalizada do GitHub Copilot](lab-041-copilot-extension.md)
- **Conectar seu participante a um servidor MCP:** → [Lab 020 — Servidor MCP em Python](lab-020-mcp-server-python.md)
