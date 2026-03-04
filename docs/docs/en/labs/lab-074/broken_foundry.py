#!/usr/bin/env python3
"""Bug-fix: Broken Foundry Analyzer - Lab 074. Fix 3 bugs."""
import io, pandas as pd
def total_requests(agents):
    # Bug #1: Returns average instead of sum
    return int(agents["requests_24h"].mean())
def count_degraded(agents):
    # Bug #2: Counts 'active' instead of 'degraded'
    return (agents["status"] == "active").sum()
def agents_without_memory(agents):
    # Bug #3: Counts cosmos_db (has memory) instead of none/session_only
    return (agents["memory_type"] == "cosmos_db").sum()
def run_tests():
    csv="agent_id,status,requests_24h,memory_type\nF1,active,1000,cosmos_db\nF2,degraded,500,session_only\nF3,active,800,none\nF4,active,1200,cosmos_db"
    a=pd.read_csv(io.StringIO(csv));p,f=0,0
    t=total_requests(a);exp=3500
    if t==exp:print(f"OK T1: {t}");p+=1
    else:print(f"FAIL T1: {t} (exp {exp})");f+=1
    d=count_degraded(a);exp=1
    if d==exp:print(f"OK T2: {d}");p+=1
    else:print(f"FAIL T2: {d} (exp {exp})");f+=1
    n=agents_without_memory(a);exp=2
    if n==exp:print(f"OK T3: {n}");p+=1
    else:print(f"FAIL T3: {n} (exp {exp})");f+=1
    print(f"\n{'All passed!' if f==0 else f'{f} failed'}")
if __name__=="__main__":
    print("Tests:\n");run_tests()
