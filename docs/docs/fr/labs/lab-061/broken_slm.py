#!/usr/bin/env python3
"""🐛 Broken SLM Analyzer — Lab 061. Fix 3 bugs, run self-tests."""
import io, pandas as pd

def slm_accuracy(bench: pd.DataFrame) -> float:
    # 🐛 Bug #1: Uses gpt4o_correct instead of phi4_mini_correct
    return bench["gpt4o_correct"].mean() * 100

def cost_savings(bench: pd.DataFrame) -> float:
    # 🐛 Bug #2: Sums tokens instead of cost — SLM cost is $0 (local)
    cloud_cost = bench["gpt4o_tokens"].sum()
    return cloud_cost

def avg_latency_by_task(bench: pd.DataFrame, task: str) -> float:
    # 🐛 Bug #3: Doesn't filter by task_type
    return bench["phi4_mini_time_ms"].mean()

def run_tests():
    csv="""\
task_id,task_type,phi4_mini_correct,phi4_mini_time_ms,phi4_mini_tokens,gpt4o_correct,gpt4o_time_ms,gpt4o_tokens,gpt4o_cost_usd
T1,classify,true,40,25,true,800,30,0.0003
T2,classify,true,35,20,true,750,28,0.0003
T3,draft,false,180,120,true,1500,150,0.0018
T4,extract,true,65,40,true,900,45,0.0005"""
    b=pd.read_csv(io.StringIO(csv))
    for c in ["phi4_mini_correct","gpt4o_correct"]:b[c]=b[c].astype(str).str.lower()=="true"
    p,f=0,0
    a=slm_accuracy(b);exp=75.0
    if abs(a-exp)<0.1:print(f"✅ Test 1 PASSED: phi4_acc={a:.1f}%");p+=1
    else:print(f"❌ Test 1 FAILED: phi4_acc={a:.1f}% (expected {exp}%)");f+=1
    c=cost_savings(b);exp=0.0029
    if abs(c-exp)<0.0001:print(f"✅ Test 2 PASSED: savings=${c:.4f}");p+=1
    else:print(f"❌ Test 2 FAILED: savings=${c} (expected ${exp})");f+=1
    l=avg_latency_by_task(b,"classify");exp=37.5
    if abs(l-exp)<0.1:print(f"✅ Test 3 PASSED: classify_lat={l:.1f}ms");p+=1
    else:print(f"❌ Test 3 FAILED: classify_lat={l:.1f}ms (expected {exp}ms)");f+=1
    print(f"\n{'🎉 All 3 tests passed!' if f==0 else f'🔧 {f} test(s) failed!'}")

if __name__=="__main__":
    print("🧪 Running self-tests…\n");run_tests()
