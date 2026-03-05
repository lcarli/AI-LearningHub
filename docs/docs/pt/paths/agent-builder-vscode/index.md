# 💻 Agent Builder — VS Code Path

<span class="level-badge level-100">L100</span> <span class="level-badge level-200">L200</span> <span class="level-badge level-300">L300</span>

Build AI agents that extend **Visual Studio Code** — turning Copilot Chat into a powerful, customizable coding assistant with domain-specific knowledge and actions.

---

## What You'll Build

- ✅ A **VS Code Chat Participant** (`@myagent`) that responds in Copilot Chat
- ✅ A chat participant that calls an **MCP Server** for live data
- ✅ Understanding of the VS Code Extension API for AI features

---

## Path Labs (1 labs, ~45 min total)

| Lab | Title | Level | Cost |
|-----|-------|-------|------|
| [Lab 025](../../labs/lab-025-vscode-chat-participant.md) | VS Code Copilot Chat Participant | <span class="level-badge level-200">L200</span> | ✅ Free |

---

## Key Concepts

### Chat Participants (`@participant`)
Chat participants are VS Code extensions that register a handler for Copilot Chat. When a user types `@myagent`, your code runs and responds.

```typescript
vscode.chat.createChatParticipant('myagent', async (request, context, stream, token) => {
    stream.markdown(`You asked: **${request.prompt}**`);
    // Call LLM, tools, MCP servers...
});
```

### VS Code Language Model API
VS Code exposes LLMs (GitHub Copilot's models) directly to extensions — no API key needed for users.

---

## Prerequisites

- VS Code 1.90+
- Node.js 20+
- GitHub Copilot extension installed

---

## External Resources

- [VS Code Chat Participants Docs](https://code.visualstudio.com/api/extension-guides/chat)
- [VS Code Language Model API](https://code.visualstudio.com/api/extension-guides/language-model)
- [VS Code Extension Samples — Chat](https://github.com/microsoft/vscode-extension-samples/tree/main/chat-sample)
