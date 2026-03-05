---
tags: [autogen, multi-agent, python, free, github-models]
---
# Lab 040 : Multi-agent en production avec AutoGen

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-400">L400</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/pro-code/">Pro Code Agents</a></span>
  <span><strong>Durée :</strong> ~90 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-github">GitHub Free</span> — GitHub Models API</span>
</div>
!!! warning "AutoGen -> Microsoft Agent Framework"
    AutoGen fait désormais partie de **Microsoft Agent Framework (MAF)**, qui unifie SK et AutoGen en un seul framework. Voir **[Lab 076 : Microsoft Agent Framework](lab-076-microsoft-agent-framework.md)** pour le guide de migration.



## Ce que vous apprendrez

- Construire un **système AutoGen à 4 agents** : Orchestrateur, Chercheur, Analyste et Critique
- Utiliser **AutoGen AgentChat** pour des conversations multi-agents structurées
- Implémenter des **conditions de terminaison** et des **stratégies de sélection**
- Concevoir des **transferts entre agents** pour des tâches complexes en plusieurs étapes
- Gérer les erreurs, les boucles et les agents bloqués de manière élégante

---

## Introduction

Microsoft **AutoGen** est un framework pour construire des systèmes multi-agents où les agents conversent pour résoudre des tâches complexes. Contrairement aux boucles à agent unique, les agents AutoGen :

- Ont des **personnalités** et des domaines d'expertise distincts
- Peuvent **critiquer** le travail des autres
- Utilisent des **transferts structurés** pour passer les tâches
- Terminent par **consensus** ou une condition d'arrêt définie

Ce lab construit un pipeline de recherche produit : étant donné une question sur un produit, l'Orchestrateur charge un Chercheur de collecter des informations, un Analyste de les structurer, et un Critique d'en vérifier la qualité.

---

## Prérequis

- Python 3.11+
- `pip install autogen-agentchat autogen-ext[openai] openai`
- `GITHUB_TOKEN` configuré

---

## Exercice pratique

### Étape 1 : Installer AutoGen

```bash
pip install autogen-agentchat autogen-ext[openai]
```

### Étape 2 : Définir le système d'agents

```python
# autogen_agents.py
import asyncio, os
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

# GitHub Models client (free, OpenAI-compatible)
model_client = OpenAIChatCompletionClient(
    model="gpt-4o-mini",
    api_key=os.environ["GITHUB_TOKEN"],
    base_url="https://models.inference.ai.azure.com",
    model_capabilities={
        "vision": False,
        "function_calling": True,
        "json_output": True,
    },
)

# --- Define agents ---

orchestrator = AssistantAgent(
    name="Orchestrator",
    model_client=model_client,
    system_message="""You are the orchestrator of a product research team.
Your job is to coordinate the team to answer customer questions about OutdoorGear Inc. products.

Workflow:
1. Ask Researcher to gather relevant product/policy information
2. Ask Analyst to structure the information clearly
3. Ask Critic to review the final answer for accuracy and completeness
4. Once Critic approves, write the final customer response
5. End with: TERMINATE

Products: TrailBlazer X200 boots ($189.99), Summit Pro Tent ($349), OmniPack 45L ($279.99), StormShell Jacket ($349), ClimbTech Harness ($129.99)
Policies: 60-day returns (unused), free shipping over $75, 2-year warranty (lifetime on climbing gear)
""",
)

researcher = AssistantAgent(
    name="Researcher",
    model_client=model_client,
    system_message="""You are the Researcher agent. When asked a product question:
1. Identify relevant products from the OutdoorGear catalog
2. Find relevant policies (returns, shipping, warranty)
3. Present raw findings as bullet points
4. Do NOT write the final answer — just gather facts""",
)

analyst = AssistantAgent(
    name="Analyst",
    model_client=model_client,
    system_message="""You are the Analyst agent. Given raw research findings:
1. Organize the information logically
2. Highlight the most relevant points for the customer's question
3. Structure as: Products → Recommendations → Relevant Policies
4. Keep it concise — no more than 150 words""",
)

critic = AssistantAgent(
    name="Critic",
    model_client=model_client,
    system_message="""You are the Critic agent. Review the Analyst's structured response:
1. Check: Does it answer the customer's actual question?
2. Check: Are the prices accurate?
3. Check: Are the policies correctly stated?
4. If good: reply "APPROVED: [brief reason]"
5. If needs work: reply "REVISION NEEDED: [specific issue]"
Do not rewrite the answer yourself.""",
)


async def run_research_team(customer_question: str):
    """Run the 4-agent team to answer a customer question."""

    # Termination: stop when Orchestrator says TERMINATE
    termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(20)

    # Use SelectorGroupChat so the orchestrator can direct who speaks next
    team = SelectorGroupChat(
        [orchestrator, researcher, analyst, critic],
        model_client=model_client,
        termination_condition=termination,
        selector_prompt="""You are managing a customer service team conversation.
Select the next agent based on what's needed:
- Orchestrator: starts, coordinates, writes final answer
- Researcher: gathers raw product/policy facts
- Analyst: structures and organizes findings
- Critic: reviews quality of structured response

Current conversation context: {history}
Available agents: {participants}
Select the next agent:""",
    )

    print(f"\n{'='*60}")
    print(f"Customer Question: {customer_question}")
    print(f"{'='*60}\n")

    await Console(team.run_stream(task=customer_question))


async def main():
    questions = [
        "I'm planning a 5-day winter backpacking trip. What gear do I need and what's the total cost?",
        "I bought boots last month but they hurt my feet. Can I return them?",
    ]
    for q in questions:
        await run_research_team(q)
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
```

```bash
python autogen_agents.py
```

### Étape 3 : Ajouter un agent de programmation

AutoGen excelle quand les agents peuvent écrire et exécuter du code. Ajoutez un agent **Codeur** :

```python
from autogen_agentchat.agents import CodeExecutorAgent
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor

coder = AssistantAgent(
    name="Coder",
    model_client=model_client,
    system_message="""You are a Python coding agent. When asked to calculate prices, 
generate reports, or process data, write and describe Python code to do it.
Always include the code in a ```python block.""",
)

# Execute code safely in a temp directory
executor = AssistantAgent(
    name="CodeExecutor",
    model_client=model_client,
    system_message="Execute the code provided by Coder and report the output.",
)
```

### Étape 4 : Gérer les erreurs et les délais d'attente

```python
import asyncio
from autogen_agentchat.base import TaskResult

async def safe_run(question: str, timeout: int = 120) -> TaskResult | None:
    try:
        return await asyncio.wait_for(run_research_team(question), timeout=timeout)
    except asyncio.TimeoutError:
        print(f"⚠️ Team timed out after {timeout}s for: {question[:50]}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
```

---

## Résumé des rôles des agents

| Agent | Rôle | Se termine quand |
|-------|------|-----------------|
| Orchestrateur | Dirige l'équipe, rédige la réponse finale | Dit « TERMINATE » |
| Chercheur | Collecte les faits bruts | Demandé par l'Orchestrateur |
| Analyste | Structure les résultats | Demandé par l'Orchestrateur |
| Critique | Revue qualité | Donne APPROVED/REVISION |

---

## Prochaines étapes

- **Extension Copilot VS Code :** → [Lab 041 — Extension Copilot personnalisée](lab-041-copilot-extension.md)
- **Ajouter l'évaluation :** → [Lab 035 — Évaluation des agents](lab-035-agent-evaluation.md)
