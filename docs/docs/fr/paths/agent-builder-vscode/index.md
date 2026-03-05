# 💻 Agent Builder — Parcours VS Code

<span class="level-badge level-100">L100</span> <span class="level-badge level-200">L200</span> <span class="level-badge level-300">L300</span>

Construisez des agents IA qui étendent **Visual Studio Code** — transformant Copilot Chat en un assistant de programmation puissant et personnalisable avec des connaissances et actions spécifiques au domaine.

---

## Ce que Vous Allez Construire

- ✅ Un **VS Code Chat Participant** (`@myagent`) qui répond dans Copilot Chat
- ✅ Un chat participant qui appelle un **Serveur MCP** pour des données en temps réel
- ✅ Compréhension de l'API d'Extensions VS Code pour les fonctionnalités IA

---

## Laboratoires du Parcours (1 laboratoire, ~45 min au total)

| Lab | Titre | Niveau | Coût |
|-----|-------|--------|------|
| [Lab 025](../../labs/lab-025-vscode-chat-participant.md) | VS Code Copilot Chat Participant | <span class="level-badge level-200">L200</span> | ✅ Free |

---

## Concepts Clés

### Chat Participants (`@participant`)
Les chat participants sont des extensions VS Code qui enregistrent un handler pour Copilot Chat. Quand un utilisateur tape `@myagent`, votre code s'exécute et répond.

```typescript
vscode.chat.createChatParticipant('myagent', async (request, context, stream, token) => {
    stream.markdown(`You asked: **${request.prompt}**`);
    // Call LLM, tools, MCP servers...
});
```

### API de Modèle de Langage VS Code
VS Code expose les LLMs (modèles de GitHub Copilot) directement aux extensions — aucune clé API nécessaire pour les utilisateurs.

---

## Prérequis

- VS Code 1.90+
- Node.js 20+
- Extension GitHub Copilot installée

---

## Ressources Externes

- [Documentation Chat Participants VS Code](https://code.visualstudio.com/api/extension-guides/chat)
- [API de Modèle de Langage VS Code](https://code.visualstudio.com/api/extension-guides/language-model)
- [Exemples d'Extensions VS Code — Chat](https://github.com/microsoft/vscode-extension-samples/tree/main/chat-sample)
