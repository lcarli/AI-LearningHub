# 💻 Agent Builder — Trilha VS Code

<span class="level-badge level-100">L100</span> <span class="level-badge level-200">L200</span> <span class="level-badge level-300">L300</span>

Construa agentes de IA que estendem o **Visual Studio Code** — transformando o Copilot Chat em um assistente de programação poderoso e personalizável com conhecimento e ações específicos do domínio.

---

## O que Você Vai Construir

- ✅ Um **VS Code Chat Participant** (`@myagent`) que responde no Copilot Chat
- ✅ Um chat participant que chama um **Servidor MCP** para dados em tempo real
- ✅ Compreensão da API de Extensões do VS Code para recursos de IA

---

## Laboratórios da Trilha (1 laboratório, ~45 min no total)

| Lab | Título | Nível | Custo |
|-----|--------|-------|-------|
| [Lab 025](../../labs/lab-025-vscode-chat-participant.md) | VS Code Copilot Chat Participant | <span class="level-badge level-200">L200</span> | ✅ Free |

---

## Conceitos Principais

### Chat Participants (`@participant`)
Chat participants são extensões do VS Code que registram um handler para o Copilot Chat. Quando um usuário digita `@myagent`, seu código é executado e responde.

```typescript
vscode.chat.createChatParticipant('myagent', async (request, context, stream, token) => {
    stream.markdown(`You asked: **${request.prompt}**`);
    // Call LLM, tools, MCP servers...
});
```

### API de Modelo de Linguagem do VS Code
O VS Code expõe LLMs (modelos do GitHub Copilot) diretamente para extensões — sem necessidade de chave de API para os usuários.

---

## Pré-requisitos

- VS Code 1.90+
- Node.js 20+
- Extensão GitHub Copilot instalada

---

## Recursos Externos

- [Documentação de Chat Participants do VS Code](https://code.visualstudio.com/api/extension-guides/chat)
- [API de Modelo de Linguagem do VS Code](https://code.visualstudio.com/api/extension-guides/language-model)
- [Exemplos de Extensões do VS Code — Chat](https://github.com/microsoft/vscode-extension-samples/tree/main/chat-sample)
