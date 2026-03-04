#!/usr/bin/env python3
"""🐛 Broken Delegation Analyzer — Lab 055. Fix 3 bugs, run self-tests."""
import io, pandas as pd

def count_a2a_calls(traces: pd.DataFrame) -> int:
    # 🐛 Bug #1: Counts ALL calls instead of filtering protocol=='A2A'
    return len(traces)

def avg_latency(traces: pd.DataFrame) -> float:
    # 🐛 Bug #2: Excludes ERROR requests — should include ALL for latency
    ok = traces[traces["status"] == "OK"]
    return ok["duration_ms"].mean()

def success_rate(traces: pd.DataFrame) -> float:
    # 🐛 Bug #3: Divides by unique source_agents instead of total requests
    ok = (traces["status"] == "OK").sum()
    return ok / traces["source_agent"].nunique() * 100

def run_tests():
    csv = """\
request_id,source_agent,target_agent,protocol,action,duration_ms,tokens_used,status
R1,Coord,AgentA,A2A,task1,2000,100,OK
R1,AgentA,tool1,MCP,call1,1000,0,OK
R2,Coord,AgentB,A2A,task2,3000,200,ERROR
R2,AgentB,tool2,MCP,call2,1500,0,OK
R3,Coord,AgentA,A2A,task3,1500,150,OK"""
    t=pd.read_csv(io.StringIO(csv));p,f=0,0
    # Test 1: A2A calls only (3, not 5)
    n=count_a2a_calls(t);exp=3
    if n==exp:print(f"✅ Test 1 PASSED: a2a={n}");p+=1
    else:print(f"❌ Test 1 FAILED: a2a={n} (expected {exp})");f+=1
    # Test 2: Avg latency all=(2000+1000+3000+1500+1500)/5=1800
    a=avg_latency(t);exp=1800.0
    if abs(a-exp)<1:print(f"✅ Test 2 PASSED: avg={a:.0f}");p+=1
    else:print(f"❌ Test 2 FAILED: avg={a:.0f} (expected {exp:.0f})");f+=1
    # Test 3: Success=4/5=80%
    r=success_rate(t);exp=80.0
    if abs(r-exp)<0.1:print(f"✅ Test 3 PASSED: rate={r:.1f}%");p+=1
    else:print(f"❌ Test 3 FAILED: rate={r:.1f}% (expected {exp:.1f}%)");f+=1
    print(f"\n{'🎉 All 3 tests passed!' if f==0 else f'🔧 {f} test(s) failed!'}")

if __name__=="__main__":
    print("🧪 Running self-tests…\n");run_tests()
