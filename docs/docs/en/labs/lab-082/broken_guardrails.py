#!/usr/bin/env python3
"""Bug-fix: Broken Guardrails Analyzer - Lab 082."""
import io, pandas as pd
def block_rate(tests):
    return (tests["action_taken"] == "passed").mean() * 100
def false_positive_count(tests):
    return (tests["false_positive"] == False).sum()
def avg_latency_blocked(tests):
    return tests["latency_added_ms"].mean()
def run_tests():
    csv="test_id,triggered,action_taken,latency_added_ms,false_positive\nG1,false,passed,12,false\nG2,true,blocked,8,false\nG3,true,redacted,15,false\nG4,true,blocked,9,false\nG5,false,passed,10,true"
    t=pd.read_csv(io.StringIO(csv))
    t["false_positive"]=t["false_positive"].astype(str).str.lower()=="true"
    p,f=0,0
    b=block_rate(t);exp=60.0
    if abs(b-exp)<0.1:print(f"OK T1: {b:.0f}%");p+=1
    else:print(f"FAIL T1: {b:.0f}% (exp {exp:.0f}%)");f+=1
    fp=false_positive_count(t);exp=1
    if fp==exp:print(f"OK T2: {fp}");p+=1
    else:print(f"FAIL T2: {fp} (exp {exp})");f+=1
    a=avg_latency_blocked(t);exp=8.5
    if abs(a-exp)<0.1:print(f"OK T3: {a:.1f}ms");p+=1
    else:print(f"FAIL T3: {a:.1f}ms (exp {exp}ms)");f+=1
    print(f"\n{'All passed!' if f==0 else f'{f} failed'}")
if __name__=="__main__":print("Tests:\n");run_tests()
