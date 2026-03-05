#!/usr/bin/env python3
"""Bug-fix: Broken Coding Tools Analyzer - Lab 081."""
import io, pandas as pd
def avg_speedup(tasks):
    return (tasks["manual_time_sec"] / tasks["copilot_cli_time_sec"]).mean()
def both_success_rate(tasks):
    return (tasks["claude_code_success"] | tasks["copilot_cli_success"]).mean() * 100
def fastest_tool(tasks):
    cc = tasks["claude_code_time_sec"].mean()
    cp = tasks["copilot_cli_time_sec"].mean()
    return "copilot_cli" if cc < cp else "claude_code"
def run_tests():
    csv="task_id,claude_code_time_sec,claude_code_success,copilot_cli_time_sec,copilot_cli_success,manual_time_sec\nT1,8,true,12,true,120\nT2,25,true,30,true,600\nT3,20,true,25,false,900"
    t=pd.read_csv(io.StringIO(csv))
    for c in ["claude_code_success","copilot_cli_success"]:t[c]=t[c].astype(str).str.lower()=="true"
    p,f=0,0
    s=avg_speedup(t);exp_cc=t["manual_time_sec"].mean()/t["claude_code_time_sec"].mean()
    if abs(s-exp_cc)<1:print(f"OK T1: {s:.1f}x");p+=1
    else:print(f"FAIL T1: {s:.1f}x (exp {exp_cc:.1f}x)");f+=1
    b=both_success_rate(t);exp=100.0
    if abs(b-exp)<0.1:print(f"OK T2: {b:.0f}%");p+=1
    else:print(f"FAIL T2: {b:.0f}% (exp {exp:.0f}%)");f+=1
    ft=fastest_tool(t);exp="claude_code"
    if ft==exp:print(f"OK T3: {ft}");p+=1
    else:print(f"FAIL T3: {ft} (exp {exp})");f+=1
    print(f"\n{'All passed!' if f==0 else f'{f} failed'}")
if __name__=="__main__":print("Tests:\n");run_tests()
