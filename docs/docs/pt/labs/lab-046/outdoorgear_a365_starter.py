"""
OutdoorGear Agent — Agent 365 Starter File
==========================================
Lab 046: Microsoft Agent 365 — Enterprise Agent Governance

This file gives you a working OutdoorGear agent skeleton with 5 TODOs for
integrating Microsoft Agent 365 SDK capabilities:
  - TODO 1: Initialize A365ObservabilityProvider
  - TODO 2: Apply OpenAI auto-instrumentation
  - TODO 3: Implement on_teams_mention handler
  - TODO 4: Connect to governed MCP tooling servers
  - TODO 5: Register Entra Agent ID

Run in mock mode (no Frontier access required):
  AGENT_365_MOCK=true python outdoorgear_a365_starter.py

Run with real Agent 365:
  AGENT_365_MOCK=false python outdoorgear_a365_starter.py
"""

import os
import asyncio
from typing import Optional

# ── Agent 365 SDK imports (install: pip install microsoft-agents-a365-*) ──────
try:
    from microsoft.agents.a365.observability.core import A365ObservabilityProvider
    from microsoft.agents.a365.observability.extensions.openai import OpenAIAgentInstrumentation
    from microsoft.agents.a365.notifications import A365NotificationHandler
    from microsoft.agents.a365.tooling import A365ToolingClient
    from microsoft.agents.a365.tooling.extensions.openai import OpenAIMcpRegistrationService
    AGENT_365_AVAILABLE = True
except ImportError:
    AGENT_365_AVAILABLE = False
    print("⚠️  Agent 365 SDK not installed. Running in mock mode.")
    print("   Install: pip install microsoft-agents-a365-observability-core "
          "microsoft-agents-a365-observability-extensions-openai "
          "microsoft-agents-a365-notifications microsoft-agents-a365-tooling\n")

# ── OpenAI Agents SDK ──────────────────────────────────────────────────────────
try:
    from openai import AsyncOpenAI
    from agents import Agent, Runner, function_tool
    OPENAI_AGENTS_AVAILABLE = True
except ImportError:
    OPENAI_AGENTS_AVAILABLE = False
    print("⚠️  OpenAI Agents SDK not installed.")
    print("   Install: pip install openai openai-agents\n")

# ── Configuration ──────────────────────────────────────────────────────────────
MOCK_MODE = os.environ.get("AGENT_365_MOCK", "true").lower() == "true"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
TENANT_ID = os.environ.get("AZURE_TENANT_ID", "mock-tenant-id")
ENTRA_AGENT_ID = os.environ.get("ENTRA_AGENT_ID", "mock-agent-id")
OTEL_ENDPOINT = os.environ.get("OTEL_ENDPOINT", "https://mock-collector.endpoint/v1/traces")

# ── OutdoorGear product catalog ────────────────────────────────────────────────
PRODUCTS = [
    {"id": "P001", "name": "TrailBlazer Tent 2P",  "category": "tent",         "price": 249.99, "in_stock": True},
    {"id": "P002", "name": "Summit Dome 4P",        "category": "tent",         "price": 549.99, "in_stock": True},
    {"id": "P003", "name": "TrailBlazer Solo",      "category": "tent",         "price": 299.99, "in_stock": False},
    {"id": "P004", "name": "ArcticDown -20°C",      "category": "sleeping bag", "price": 389.99, "in_stock": True},
    {"id": "P005", "name": "SummerLight +5°C",      "category": "sleeping bag", "price": 149.99, "in_stock": True},
    {"id": "P006", "name": "Osprey Atmos 65L",      "category": "backpack",     "price": 289.99, "in_stock": True},
    {"id": "P007", "name": "DayHiker 22L",           "category": "backpack",     "price": 89.99,  "in_stock": True},
]


# ── Agent tools ────────────────────────────────────────────────────────────────
def search_products(query: str, category: Optional[str] = None) -> list:
    """Search OutdoorGear products by keyword and optional category."""
    results = PRODUCTS
    if category:
        results = [p for p in results if category.lower() in p["category"].lower()]
    if query:
        results = [p for p in results if query.lower() in p["name"].lower()
                   or query.lower() in p["category"].lower()]
    return results


def get_product_details(product_id: str) -> dict:
    """Get full details for a specific product by ID."""
    for p in PRODUCTS:
        if p["id"].upper() == product_id.upper():
            return p
    return {"error": f"Product {product_id} not found"}


def check_inventory(category: str) -> dict:
    """Get inventory summary for a product category."""
    items = [p for p in PRODUCTS if category.lower() in p["category"].lower()]
    in_stock = [p for p in items if p["in_stock"]]
    out_of_stock = [p for p in items if not p["in_stock"]]
    return {
        "category": category,
        "total": len(items),
        "in_stock": len(in_stock),
        "out_of_stock": len(out_of_stock),
        "items": items
    }


# ─────────────────────────────────────────────────────────────────────────────
# TODO 1: Initialize A365ObservabilityProvider
# ─────────────────────────────────────────────────────────────────────────────
# Replace this mock with real initialization:
#
#   observability = A365ObservabilityProvider(
#       service_name="OutdoorGearAgent",
#       service_version="1.0.0",
#       exporter_endpoint=OTEL_ENDPOINT
#   )
#
# In mock mode, we use a simple print-based tracer:

class MockObservabilityProvider:
    def __init__(self, service_name: str):
        self.service_name = service_name
        print(f"[MOCK] ObservabilityProvider initialized: {service_name}")

    def start_span(self, name: str):
        print(f"[MOCK TRACE] → {name}")
        return self

    def __enter__(self): return self
    def __exit__(self, *args): pass


def init_observability():
    """TODO 1: Replace with real A365ObservabilityProvider initialization."""
    if MOCK_MODE or not AGENT_365_AVAILABLE:
        return MockObservabilityProvider(service_name="OutdoorGearAgent")
    
    # TODO 1: Uncomment and fill in:
    # return A365ObservabilityProvider(
    #     service_name="OutdoorGearAgent",
    #     service_version="1.0.0",
    #     exporter_endpoint=OTEL_ENDPOINT
    # )
    raise NotImplementedError("TODO 1: Initialize A365ObservabilityProvider")


# ─────────────────────────────────────────────────────────────────────────────
# TODO 2: Apply OpenAI Agents SDK auto-instrumentation
# ─────────────────────────────────────────────────────────────────────────────
# After creating the observability provider, instrument the SDK so every
# agent run is automatically traced:
#
#   instrumentation = OpenAIAgentInstrumentation(provider=observability)
#   instrumentation.instrument()

def apply_instrumentation(observability_provider):
    """TODO 2: Replace with real OpenAIAgentInstrumentation."""
    if MOCK_MODE or not AGENT_365_AVAILABLE:
        print("[MOCK] Auto-instrumentation active (mock traces only)")
        return
    
    # TODO 2: Uncomment and fill in:
    # instrumentation = OpenAIAgentInstrumentation(provider=observability_provider)
    # instrumentation.instrument()
    raise NotImplementedError("TODO 2: Apply OpenAIAgentInstrumentation")


# ─────────────────────────────────────────────────────────────────────────────
# TODO 3: Implement Teams notification handler
# ─────────────────────────────────────────────────────────────────────────────
# When a user @mentions the agent in Teams, this handler fires.
# Subclass A365NotificationHandler and override on_teams_mention().

class OutdoorGearNotificationHandler:
    """
    TODO 3: When not in mock mode, inherit from A365NotificationHandler:
    
        class OutdoorGearNotificationHandler(A365NotificationHandler):
            async def on_teams_mention(self, context):
                user_message = context.activity.text
                response = await Runner.run(agent, input=user_message)
                await context.send_activity(response.final_output)
    """
    
    def __init__(self, agent):
        self.agent = agent
    
    async def on_teams_mention(self, context=None, message: str = ""):
        """Handle @mention in Teams."""
        # In mock mode, we simulate a Teams message
        print(f"\n[MOCK TEAMS] @OutdoorGearAgent: {message}")
        # TODO 3: In real mode, get message from context.activity.text
        # and use context.send_activity() to reply
        return f"Mock response to: {message}"
    
    async def on_email_received(self, context=None, subject: str = "", body: str = ""):
        """Handle email to agent mailbox."""
        print(f"\n[MOCK EMAIL] Subject: {subject}\nBody: {body}")
        return f"Mock email response to: {subject}"


# ─────────────────────────────────────────────────────────────────────────────
# TODO 4: Connect to governed M365 MCP tooling servers
# ─────────────────────────────────────────────────────────────────────────────
# In production, this grants your agent access to Mail, Calendar, Teams, etc.
# under IT-governed policies defined in your Blueprint.
#
#   tooling_client = A365ToolingClient(
#       agent_id=ENTRA_AGENT_ID,
#       tenant_id=TENANT_ID
#   )
#   mcp_servers = await tooling_client.get_mcp_servers()
#   registration_service = OpenAIMcpRegistrationService(agent)
#   for server in mcp_servers:
#       await registration_service.register(server)

async def connect_m365_tools(agent):
    """TODO 4: Connect governed MCP tools to agent."""
    if MOCK_MODE or not AGENT_365_AVAILABLE:
        print("[MOCK] M365 MCP tools connected (mock): mail.read, calendar.readwrite, teams.message.send")
        return agent
    
    # TODO 4: Uncomment and fill in:
    # tooling_client = A365ToolingClient(
    #     agent_id=ENTRA_AGENT_ID,
    #     tenant_id=TENANT_ID
    # )
    # mcp_servers = await tooling_client.get_mcp_servers()
    # registration_service = OpenAIMcpRegistrationService(agent)
    # for server in mcp_servers:
    #     await registration_service.register(server)
    raise NotImplementedError("TODO 4: Connect M365 MCP tools")


# ─────────────────────────────────────────────────────────────────────────────
# TODO 5: Register Entra Agent ID
# ─────────────────────────────────────────────────────────────────────────────
# Tell the Agent 365 runtime which Entra Agent ID this agent uses.
# This ties the agent's identity to the blueprint and observability traces.
#
# In real code, typically done via environment variable ENTRA_AGENT_ID
# or by reading from a365.config.json at startup.

def register_agent_identity(agent_id: str = ENTRA_AGENT_ID):
    """TODO 5: Register the Entra Agent ID for this agent instance."""
    if MOCK_MODE:
        print(f"[MOCK] Entra Agent ID registered: {agent_id}")
        return agent_id
    
    # TODO 5: In production, validate the agent_id against your tenant:
    # from microsoft.agents.a365.runtime import A365Runtime
    # runtime = A365Runtime(tenant_id=TENANT_ID)
    # runtime.set_agent_id(agent_id)
    # return runtime.validate_agent_id()
    
    print(f"[INFO] Entra Agent ID: {agent_id}")
    return agent_id


# ─────────────────────────────────────────────────────────────────────────────
# Main agent setup & demo
# ─────────────────────────────────────────────────────────────────────────────

async def build_agent():
    """Build and configure the OutdoorGear Agent with Agent 365 capabilities."""
    
    print("=" * 60)
    print("  OutdoorGear Agent — Microsoft Agent 365 Starter")
    print(f"  Mode: {'🔵 MOCK' if MOCK_MODE else '🟢 PRODUCTION'}")
    print("=" * 60)
    
    # Step 1 & 2: Observability
    observability = init_observability()
    apply_instrumentation(observability)
    
    # Step 5: Register identity
    agent_id = register_agent_identity()
    
    if not OPENAI_AGENTS_AVAILABLE:
        print("\n⚠️  OpenAI Agents SDK not available — skipping agent creation")
        print("   Install: pip install openai openai-agents")
        return None, None
    
    # Build the agent with OutdoorGear tools
    client = AsyncOpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=GITHUB_TOKEN or "mock-key"
    ) if GITHUB_TOKEN else None
    
    # Define tools for the agent
    tools = [
        function_tool(search_products),
        function_tool(get_product_details),
        function_tool(check_inventory),
    ]
    
    agent = Agent(
        name="OutdoorGearAgent",
        instructions="""You are the OutdoorGear Assistant, an enterprise AI agent 
        for the OutdoorGear retail chain. Help employees find products, check 
        inventory, and answer product questions. You are governed by Microsoft 
        Agent 365, which means your actions are logged, auditable, and controlled 
        by IT policies.
        
        Always be concise and factual. Only answer questions about OutdoorGear products.""",
        tools=tools,
        model="gpt-4o-mini"
    )
    
    # Step 4: Connect M365 tools (mock in demo mode)
    if MOCK_MODE:
        print("[MOCK] M365 MCP tools connected (mock): mail.read, calendar.readwrite, teams.message.send")
    else:
        agent = await connect_m365_tools(agent)
    
    # Create notification handler
    handler = OutdoorGearNotificationHandler(agent)
    
    print(f"\n✅ Agent built: {agent.name}")
    print(f"   Entra Agent ID: {agent_id}")
    print(f"   Tools: {[t.name for t in tools]}")
    print(f"   Governed MCP: mail.read, calendar.readwrite, teams.message.send")
    
    return agent, handler


async def run_demo(agent, handler):
    """Run a mock demo simulating Teams @mentions and direct queries."""
    
    if not agent:
        return
    
    print("\n" + "=" * 60)
    print("  Demo: Simulated Agent 365 Interactions")
    print("=" * 60)
    
    # Simulate a Teams @mention
    print("\n📨 Simulating Teams @mention...")
    await handler.on_teams_mention(
        message="What tents do you have in stock under $300?"
    )
    
    # Simulate a direct query (would come through Runner in production)
    print("\n🔍 Direct agent query (local test)...")
    if GITHUB_TOKEN:
        result = await Runner.run(
            agent,
            input="How many backpacks are in stock?"
        )
        print(f"Agent response: {result.final_output}")
    else:
        print("[SKIPPED] No GITHUB_TOKEN — set GITHUB_TOKEN to test real queries")
        # Manually call the tool to demonstrate
        inventory = check_inventory("backpack")
        print(f"[MOCK ANSWER] Backpack inventory: {inventory['in_stock']} in stock, "
              f"{inventory['out_of_stock']} out of stock")
    
    # Simulate receiving an email
    print("\n📧 Simulating email to agent mailbox...")
    await handler.on_email_received(
        subject="Inquiry: Camping Tents for Team Retreat",
        body="Hi, we need 5 tents for a company retreat. What do you recommend?"
    )
    
    print("\n✅ Demo complete!")
    print("\nNext steps to go to production:")
    print("  1. Complete the 5 TODOs in this file")
    print("  2. Install real Agent 365 SDK packages")
    print("  3. Run: a365 config init")
    print("  4. Run: a365 setup")
    print("  5. Run: a365 deploy && a365 publish")


if __name__ == "__main__":
    async def main():
        agent, handler = await build_agent()
        await run_demo(agent, handler)
    
    asyncio.run(main())
