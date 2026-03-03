# 🧠 Semantic Kernel Path

<span class="level-badge level-100">L100</span> <span class="level-badge level-200">L200</span> <span class="level-badge level-300">L300</span> <span class="level-badge level-400">L400</span>

Semantic Kernel (SK) is Microsoft's open-source SDK for building AI agents and applications in **Python**, **C#**, and **Java**. It provides a rich abstraction layer over LLMs with support for plugins, memory, vector stores, auto function calling, and multi-agent orchestration.

---

## What You'll Build

- ✅ Your first SK agent powered by **GitHub Models (free)**
- ✅ **Plugins** (native functions + OpenAPI connectors)
- ✅ **Vector memory** for context-aware agents
- ✅ **Auto function calling** with planners
- ✅ **Multi-agent orchestration** with an orchestrator + worker pattern

---

## Path Labs

| Lab | Title | Level | Cost |
|-----|-------|-------|------|
| [Lab 014](../../labs/lab-014-sk-hello-agent.md) | SK Hello Agent | <span class="level-badge level-100">L100</span> | ✅ Free (GitHub Models) |
| [Lab 023](../../labs/lab-023-sk-plugins-memory.md) | SK Plugins, Memory & Planners | <span class="level-badge level-200">L200</span> | ✅ Free (GitHub Models) |
| [Lab 034](../../labs/lab-034-multi-agent-sk.md) | Multi-Agent Orchestration with SK | <span class="level-badge level-300">L300</span> | ⚠️ Azure sub |

---

## Semantic Kernel Building Blocks

```
┌─────────────────────────────────────────────────┐
│                 Semantic Kernel                 │
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │  Kernel  │  │ Plugins  │  │ Vector Store │  │
│  │ (LLM +  │  │(functions│  │  (memory)    │  │
│  │ services)│  │+ prompts)│  │              │  │
│  └──────────┘  └──────────┘  └──────────────┘  │
│                                                 │
│  ┌──────────────────────────────────────────┐   │
│  │         Auto Function Calling            │   │
│  │  (LLM decides which plugins to invoke)   │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

---

## External Resources

- [Semantic Kernel GitHub](https://github.com/microsoft/semantic-kernel)
- [SK Docs](https://learn.microsoft.com/semantic-kernel/)
- [SK Cookbook (Python)](https://github.com/microsoft/semantic-kernel/tree/main/python/samples)
- [SK Cookbook (C#)](https://github.com/microsoft/semantic-kernel/tree/main/dotnet/samples)
