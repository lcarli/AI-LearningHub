#!/usr/bin/env python3
"""🐛 Broken Safety Analyzer — Lab 057. Fix 3 bugs, run self-tests."""
import io, pandas as pd

def completion_rate(tasks: pd.DataFrame) -> float:
    # 🐛 Bug #1: Counts all tasks as denominator including non-attempted
    #   Should count completed/total, but uses len(completed) / len(completed)
    completed = tasks[tasks["completed"] == True]
    return len(completed) / len(completed) * 100

def count_high_risk(tasks: pd.DataFrame) -> int:
    # 🐛 Bug #2: Checks for 'medium' instead of 'high' safety_risk
    return (tasks["safety_risk"] == "medium").sum()

def avg_time_completed(tasks: pd.DataFrame) -> float:
    # 🐛 Bug #3: Averages ALL tasks instead of only completed ones
    return tasks["time_sec"].mean()

def run_tests():
    csv="""\
task_id,completed,time_sec,safety_risk
T1,true,12,low
T2,true,18,low
T3,false,60,high
T4,true,30,medium
T5,false,55,high"""
    t=pd.read_csv(io.StringIO(csv));t["completed"]=t["completed"].astype(str).str.lower()=="true"
    p,f=0,0
    r=completion_rate(t);exp=60.0  # 3/5
    if abs(r-exp)<0.1:print(f"✅ Test 1 PASSED: rate={r:.1f}%");p+=1
    else:print(f"❌ Test 1 FAILED: rate={r:.1f}% (expected {exp}%)");f+=1
    h=count_high_risk(t);exp=2
    if h==exp:print(f"✅ Test 2 PASSED: high_risk={h}");p+=1
    else:print(f"❌ Test 2 FAILED: high_risk={h} (expected {exp})");f+=1
    a=avg_time_completed(t);exp=20.0  # (12+18+30)/3
    if abs(a-exp)<0.1:print(f"✅ Test 3 PASSED: avg_time={a:.1f}s");p+=1
    else:print(f"❌ Test 3 FAILED: avg_time={a:.1f}s (expected {exp}s)");f+=1
    print(f"\n{'🎉 All 3 tests passed!' if f==0 else f'🔧 {f} test(s) failed!'}")

if __name__=="__main__":
    print("🧪 Running self-tests…\n");run_tests()
