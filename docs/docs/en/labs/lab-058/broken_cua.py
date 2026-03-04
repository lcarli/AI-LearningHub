#!/usr/bin/env python3
"""🐛 Broken CUA Analyzer — Lab 058. Fix 3 bugs, run self-tests."""
import io, pandas as pd

def cua_success_rate(tasks: pd.DataFrame) -> float:
    # 🐛 Bug #1: Uses playwright_completed instead of cua_completed
    return tasks["playwright_completed"].mean() * 100

def total_screenshots(tasks: pd.DataFrame) -> int:
    # 🐛 Bug #2: Uses max() instead of sum()
    return int(tasks["cua_screenshots"].max())

def avg_time_by_difficulty(tasks: pd.DataFrame, difficulty: str) -> float:
    # 🐛 Bug #3: Doesn't filter by difficulty — averages all tasks
    return tasks["cua_time_sec"].mean()

def run_tests():
    csv="""\
task_id,difficulty,cua_completed,cua_time_sec,cua_screenshots,playwright_completed
T1,easy,true,8,3,true
T2,easy,true,12,5,true
T3,hard,false,45,18,true
T4,hard,true,35,14,false"""
    t=pd.read_csv(io.StringIO(csv));t["cua_completed"]=t["cua_completed"].astype(str).str.lower()=="true"
    t["playwright_completed"]=t["playwright_completed"].astype(str).str.lower()=="true"
    p,f=0,0
    r=cua_success_rate(t);exp=75.0  # 3/4
    if abs(r-exp)<0.1:print(f"✅ Test 1 PASSED: cua_rate={r:.1f}%");p+=1
    else:print(f"❌ Test 1 FAILED: cua_rate={r:.1f}% (expected {exp}%)");f+=1
    s=total_screenshots(t);exp=40  # 3+5+18+14
    if s==exp:print(f"✅ Test 2 PASSED: screenshots={s}");p+=1
    else:print(f"❌ Test 2 FAILED: screenshots={s} (expected {exp})");f+=1
    a=avg_time_by_difficulty(t,"easy");exp=10.0  # (8+12)/2
    if abs(a-exp)<0.1:print(f"✅ Test 3 PASSED: avg_easy={a:.1f}s");p+=1
    else:print(f"❌ Test 3 FAILED: avg_easy={a:.1f}s (expected {exp}s)");f+=1
    print(f"\n{'🎉 All 3 tests passed!' if f==0 else f'🔧 {f} test(s) failed!'}")

if __name__=="__main__":
    print("🧪 Running self-tests…\n");run_tests()
