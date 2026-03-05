---
tags: [autogen, multi-agent, python, free, github-models]
---
# Lab 040: Production Multi-Agent with AutoGen

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-400">L400</span></span>
  <span><strong>Path:</strong> <a href="../paths/pro-code/">Pro Code Agents</a></span>
  <span><strong>Time:</strong> ~90 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-github">GitHub Free</span> — GitHub Models API</span>
</div>

!!! info "Traduction en cours"
    Ce lab est en cours de traduction. Le contenu ci-dessous est en anglais.


!!! warning "AutoGen -> Microsoft Agent Framework"
    AutoGen is now part of **Microsoft Agent Framework (MAF)**, which unifies SK and AutoGen into a single framework. See **[Lab 076: Microsoft Agent Framework](lab-076-microsoft-agent-framework.md)** for the migration guide.



## What You'll Learn

- Build a **4-agent AutoGen system**: Orchestrator, Researcher, Analyst, and Critic
- Use **AutoGen AgentChat** for structured multi-agent conversations
- Implement **termination conditions** and **selection strategies**
- Design **agent handoffs** for complex multi-step tasks
- Handle errors, loops, and stuck agents gracefully

---

## Introduction

Microsoft **AutoGen** is a framework for building multi-agent systems where agents converse to solve complex tasks. Unlike single-agent loops, AutoGen agents:

- Have distinct **personas** and expertise areas
- Can **critique** each other's work
- Use **structured handoffs** to pass tasks
- Terminate with **consensus** or a defined stop condition

This lab builds a product research pipeline: given a product question, the Orchestrator tasks a Researcher to gather info, an Analyst to structure it, and a Critic to review quality.

---

## Prerequisites

- Python 3.11+
- `pip install autogen-agentchat autogen-ext[openai] openai`
- `GITHUB_TOKEN` set

---

## Lab Exercise

### Step 1: Install AutoGen

```bash
pip install autogen-agentchat autogen-ext[openai]
```

### Step 2: Define the agent system

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

### Step 3: Add a code-writing agent

AutoGen shines when agents can write and execute code. Add a **Coder** agent:

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

### Step 4: Handle errors and timeouts

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

## Agent Roles Summary

| Agent | Role | Terminates when |
|-------|------|-----------------|
| Orchestrator | Directs team, writes final answer | Says "TERMINATE" |
| Researcher | Gathers raw facts | Asked to by Orchestrator |
| Analyst | Structures findings | Asked to by Orchestrator |
| Critic | Quality review | Gives APPROVED/REVISION |

---

## Next Steps

- **VS Code Copilot Extension:** → [Lab 041 — Custom Copilot Extension](lab-041-copilot-extension.md)
- **Add evaluation:** → [Lab 035 — Agent Evaluation](lab-035-agent-evaluation.md)
