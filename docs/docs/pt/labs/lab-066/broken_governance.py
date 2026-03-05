#!/usr/bin/env python3
"""Bug-fix: Broken Governance Analyzer - Lab 066. Fix 3 bugs."""
import io, pandas as pd
def count_failed_scans(agents):
    # Bug #1: Counts 'passed' instead of 'failed'
    return (agents["security_scan"] == "passed").sum()
def count_citizen_agents(agents):
    # Bug #2: Counts pro_dev instead of citizen
    return (agents["creator_type"] == "pro_dev").sum()
def unprotected_published(agents):
    # Bug #3: Missing published=True filter
    return len(agents[agents["runtime_protection"] == "unprotected"])
def run_tests():
    csv="agent_id,creator_type,security_scan,runtime_protection,published\nA1,citizen,failed,unprotected,true\nA2,citizen,passed,protected,true\nA3,pro_dev,failed,unprotected,false\nA4,citizen,warning,partial,true"
    a=pd.read_csv(io.StringIO(csv));p,f=0,0
    n=count_failed_scans(a);exp=2
    if n==exp:print(f"OK T1: {n}");p+=1
    else:print(f"FAIL T1: {n} (exp {exp})");f+=1
    c=count_citizen_agents(a);exp=3
    if c==exp:print(f"OK T2: {c}");p+=1
    else:print(f"FAIL T2: {c} (exp {exp})");f+=1
    u=unprotected_published(a);exp=1
    if u==exp:print(f"OK T3: {u}");p+=1
    else:print(f"FAIL T3: {u} (exp {exp})");f+=1
    print(f"\n{'All passed!' if f==0 else f'{f} failed'}")
if __name__=="__main__":
    print("Tests:\n");run_tests()
