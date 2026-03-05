#!/usr/bin/env python3
"""Bug-fix: Broken Benchmark Analyzer - Lab 073. Fix 3 bugs."""
import io, pandas as pd
def best_agent(results):
    # Bug #1: Returns agent with lowest resolve rate instead of highest
    return results.loc[results["resolve_rate_pct"].idxmin(), "agent_name"]
def avg_cost_per_resolve(results):
    # Bug #2: Divides total cost by total issues instead of resolved
    return results["avg_cost_usd"].sum() / results["total_issues"].sum()
def agentic_vs_baseline(results, model):
    # Bug #3: Doesn't filter by model
    agentic=results[results["strategy"]=="agentic_loop"]["resolve_rate_pct"].mean()
    baseline=results[results["strategy"]=="direct_prompt"]["resolve_rate_pct"].mean()
    return agentic - baseline
def run_tests():
    csv="agent_id,agent_name,model,total_issues,resolved,resolve_rate_pct,avg_cost_usd,strategy\nA1,Base GPT,gpt-4o,100,30,30.0,0.85,direct_prompt\nA2,Agent GPT,gpt-4o,100,50,50.0,2.50,agentic_loop\nA3,Base o3,o3,100,45,45.0,3.00,direct_prompt\nA4,Agent o3,o3,100,65,65.0,5.50,agentic_loop"
    r=pd.read_csv(io.StringIO(csv));p,f=0,0
    b=best_agent(r);exp="Agent o3"
    if b==exp:print(f"OK T1: {b}");p+=1
    else:print(f"FAIL T1: {b} (exp {exp})");f+=1
    c=avg_cost_per_resolve(r);exp=sum([0.85,2.50,3.00,5.50])/sum([30,50,45,65])
    if abs(c-exp)<0.001:print(f"OK T2: {c:.4f}");p+=1
    else:print(f"FAIL T2: {c:.4f} (exp {exp:.4f})");f+=1
    d=agentic_vs_baseline(r,"gpt-4o");exp=20.0
    if abs(d-exp)<0.1:print(f"OK T3: {d}");p+=1
    else:print(f"FAIL T3: {d} (exp {exp})");f+=1
    print(f"\n{'All passed!' if f==0 else f'{f} failed'}")
if __name__=="__main__":
    print("Tests:\n");run_tests()
