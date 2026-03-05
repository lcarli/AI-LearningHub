#!/usr/bin/env python3
"""Bug-fix: Broken Power BI Analyzer - Lab 075. Fix 3 bugs."""
import io, pandas as pd
def count_copilot_reports(reports):
    # Bug #1: Counts only 'manual' instead of copilot methods
    return (reports["creation_method"] == "manual").sum()
def total_time_saved(reports):
    # Bug #2: Averages instead of summing time_saved_min
    return reports["time_saved_min"].mean()
def avg_accuracy_by_method(reports, method):
    # Bug #3: Doesn't filter by method
    return reports["accuracy_score"].mean()
def run_tests():
    csv="report_id,creation_method,time_saved_min,accuracy_score\nR1,manual,0,0.95\nR2,copilot_assisted,45,0.92\nR3,copilot_generated,60,0.88\nR4,copilot_assisted,30,0.94"
    r=pd.read_csv(io.StringIO(csv));p,f=0,0
    c=count_copilot_reports(r);exp=3
    if c==exp:print(f"OK T1: {c}");p+=1
    else:print(f"FAIL T1: {c} (exp {exp})");f+=1
    t=total_time_saved(r);exp=135.0
    if abs(t-exp)<0.1:print(f"OK T2: {t}");p+=1
    else:print(f"FAIL T2: {t} (exp {exp})");f+=1
    a=avg_accuracy_by_method(r,"copilot_generated");exp=0.88
    if abs(a-exp)<0.01:print(f"OK T3: {a}");p+=1
    else:print(f"FAIL T3: {a} (exp {exp})");f+=1
    print(f"\n{'All passed!' if f==0 else f'{f} failed'}")
if __name__=="__main__":
    print("Tests:\n");run_tests()
