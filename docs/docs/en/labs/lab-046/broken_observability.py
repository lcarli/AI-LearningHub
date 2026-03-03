"""
Broken Observability Setup — Bug-Fix Exercise
==============================================
Lab 046: Microsoft Agent 365 — Enterprise Agent Governance

This file has 3 intentional bugs in the Agent 365 observability setup.
Find and fix them all, then run the self-test at the bottom.

Run with:
  python lab-046/broken_observability.py
"""

# ── Mock Agent 365 SDK classes (simulates real SDK for the exercise) ──────────
# In the real lab you'd import from microsoft.agents.a365.*

class A365ObservabilityProvider:
    """Simulated Agent 365 observability provider."""
    
    def __init__(self, service_name: str, service_version: str, exporter_endpoint: str):
        if not service_name:
            raise ValueError("service_name is required and cannot be empty")
        if not exporter_endpoint.startswith("https://"):
            raise ConnectionRefusedError(
                f"Invalid exporter endpoint: '{exporter_endpoint}'. "
                f"Must start with https:// (got: {exporter_endpoint})"
            )
        self.service_name = service_name
        self.service_version = service_version
        self.exporter_endpoint = exporter_endpoint
        self._initialized = True
    
    @property
    def is_initialized(self):
        return self._initialized


class OpenAIAgentInstrumentation:
    """Simulated OpenAI Agents SDK instrumentation for Agent 365."""
    
    def __init__(self, provider: A365ObservabilityProvider):
        if not isinstance(provider, A365ObservabilityProvider):
            raise TypeError(
                f"provider must be an A365ObservabilityProvider instance, "
                f"got {type(provider).__name__}"
            )
        if not provider.is_initialized:
            raise RuntimeError("ObservabilityProvider must be initialized before instrumenting")
        self._provider = provider
        self._instrumented = False
    
    def instrument(self):
        self._instrumented = True
    
    @property
    def service_name(self):
        return self._provider.service_name if self._instrumented else "unknown"
    
    @property
    def is_active(self):
        return self._instrumented


# ── BUGGY setup code — find and fix 3 bugs! ───────────────────────────────────
#
# The developer wrote this setup code with 3 mistakes.
# The bugs are marked with comments but NOT all in obvious places.
# Read carefully!


def setup_observability():
    """
    Initialize Agent 365 observability for the OutdoorGear Agent.
    
    BUG HUNT:
    - Bug #1: A365ObservabilityProvider is initialized incorrectly — missing a required argument
    - Bug #2: OpenAIAgentInstrumentation is not receiving the provider it needs
    - Bug #3: The exporter endpoint is wrong — it uses localhost instead of HTTPS
    """
    
    # BUG #1 is here — look carefully at the arguments
    observability = A365ObservabilityProvider(
        service_version="1.0.0",
        exporter_endpoint="https://my-otel-collector.azure.com/v1/traces"
        # Missing: service_name="OutdoorGearAgent"
    )
    
    # BUG #2 is here — the instrumentation is not connected to the provider
    instrumentation = OpenAIAgentInstrumentation(provider=None)  # should be: provider=observability
    instrumentation.instrument()
    
    # BUG #3 is here — wrong endpoint scheme
    bad_endpoint_observability = A365ObservabilityProvider(
        service_name="OutdoorGearAgent",
        service_version="1.0.0",
        exporter_endpoint="localhost:4317"  # should start with https://
    )
    
    return observability, instrumentation


# ── Self-test runner ────────────────────────────────────────────────────────────

def run_tests():
    """Run all tests. After fixing the 3 bugs, all tests should pass."""
    
    passed = 0
    failed = 0
    
    print("=" * 55)
    print("  Agent 365 Observability — Bug-Fix Self-Test")
    print("=" * 55)
    
    # Test 1: Provider initializes with service_name
    print("\nTest 1: A365ObservabilityProvider has correct service_name...")
    try:
        provider = A365ObservabilityProvider(
            service_name="OutdoorGearAgent",
            service_version="1.0.0",
            exporter_endpoint="https://my-collector.azure.com/v1/traces"
        )
        assert provider.service_name == "OutdoorGearAgent", \
            f"Expected 'OutdoorGearAgent', got '{provider.service_name}'"
        print("  ✅ Passed — service_name = OutdoorGearAgent")
        passed += 1
    except Exception as e:
        print(f"  ❌ Failed — {e}")
        failed += 1
    
    # Test 2: Instrumentation correctly reflects service_name
    print("\nTest 2: Instrumentation reports service_name: OutdoorGearAgent...")
    try:
        provider = A365ObservabilityProvider(
            service_name="OutdoorGearAgent",
            service_version="1.0.0",
            exporter_endpoint="https://my-collector.azure.com/v1/traces"
        )
        instr = OpenAIAgentInstrumentation(provider=provider)
        instr.instrument()
        assert instr.service_name == "OutdoorGearAgent", \
            f"Expected 'OutdoorGearAgent', got '{instr.service_name}'"
        assert instr.is_active, "Instrumentation should be active after .instrument()"
        print("  ✅ Passed — service_name correctly propagated from provider")
        passed += 1
    except Exception as e:
        print(f"  ❌ Failed — {e}")
        failed += 1
    
    # Test 3: Endpoint validation
    print("\nTest 3: Exporter endpoint must start with https://...")
    try:
        # This should FAIL (raise ConnectionRefusedError)
        bad = A365ObservabilityProvider(
            service_name="test",
            service_version="1.0.0",
            exporter_endpoint="localhost:4317"
        )
        print("  ❌ Failed — should have raised ConnectionRefusedError for localhost endpoint")
        failed += 1
    except ConnectionRefusedError:
        print("  ✅ Passed — correctly rejected localhost endpoint")
        passed += 1
    except Exception as e:
        print(f"  ❌ Failed — unexpected error: {e}")
        failed += 1
    
    # Test 4: Full happy-path setup
    print("\nTest 4: Full observability setup (no bugs)...")
    try:
        provider = A365ObservabilityProvider(
            service_name="OutdoorGearAgent",
            service_version="1.0.0",
            exporter_endpoint="https://otel-collector.azure.com/v1/traces"
        )
        instr = OpenAIAgentInstrumentation(provider=provider)
        instr.instrument()
        assert provider.is_initialized
        assert instr.is_active
        assert instr.service_name == "OutdoorGearAgent"
        print("  ✅ Passed — full setup works correctly")
        passed += 1
    except Exception as e:
        print(f"  ❌ Failed — {e}")
        failed += 1
    
    # Summary
    print("\n" + "=" * 55)
    print(f"  Results: {passed} passed, {failed} failed")
    print("=" * 55)
    
    if failed == 0:
        print("\n🎉 All tests passed! Your observability setup is bug-free.")
        print("\nWhat you fixed:")
        print("  Bug #1: Added missing service_name='OutdoorGearAgent' to A365ObservabilityProvider")
        print("  Bug #2: Changed provider=None to provider=observability in OpenAIAgentInstrumentation")
        print("  Bug #3: Changed 'localhost:4317' to a valid https:// endpoint")
    else:
        print(f"\n⚠️  {failed} test(s) still failing. Keep debugging!")
        print("\nHints:")
        print("  Bug #1: Look at what arguments A365ObservabilityProvider __init__ requires")
        print("  Bug #2: What should be passed to OpenAIAgentInstrumentation(provider=...)?")
        print("  Bug #3: What scheme does a valid OTEL exporter endpoint require?")
    
    return failed == 0


if __name__ == "__main__":
    print("Running tests on BUGGY setup_observability()...")
    print("(The tests test the CORRECTED behavior — your job is to fix setup_observability)\n")
    
    # First, demonstrate the bugs
    print("Current buggy setup_observability() output:")
    try:
        obs, instr = setup_observability()
        print(f"  observability.service_name = '{getattr(obs, 'service_name', 'MISSING')}'")
        print(f"  instrumentation.service_name = '{instr.service_name}'")
    except Exception as e:
        print(f"  ❌ Error in setup_observability(): {e}")
    
    print("\n" + "-" * 55)
    print("Running correctness tests (these define the target behavior):")
    print("-" * 55)
    
    run_tests()
