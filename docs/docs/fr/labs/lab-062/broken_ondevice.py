#!/usr/bin/env python3
"""🐛 Broken On-Device Analyzer — Lab 062. Fix 3 bugs, run self-tests."""
import io, pandas as pd

def npu_success_rate(tasks: pd.DataFrame) -> float:
    # 🐛 Bug #1: Counts quality_match instead of npu_available tasks that succeeded
    return tasks["quality_match"].mean() * 100

def speedup_ratio(tasks: pd.DataFrame) -> float:
    # 🐛 Bug #2: Divides NPU by cloud (should be cloud/NPU for speedup)
    return tasks["npu_time_ms"].mean() / tasks["cloud_time_ms"].mean()

def count_unavailable(tasks: pd.DataFrame) -> int:
    # 🐛 Bug #3: Counts npu_available=True instead of False
    return (tasks["npu_available"] == True).sum()

def run_tests():
    csv="""\
task_id,task_type,npu_time_ms,cloud_time_ms,npu_available,quality_match
T1,classify,30,800,true,true
T2,classify,25,750,true,true
T3,summarize,90,1200,true,false
T4,rewrite,110,1100,false,false
T5,classify,28,780,true,true"""
    t=pd.read_csv(io.StringIO(csv))
    for c in ["npu_available","quality_match"]:t[c]=t[c].astype(str).str.lower()=="true"
    p,f=0,0
    # NPU available tasks: T1,T2,T3,T5 = 4. Of those, T1,T2,T5 have quality_match=True → 3/4=75%
    # But we want: tasks where npu_available=True → success rate based on quality_match among those
    npu_tasks=t[t["npu_available"]==True]
    r=npu_success_rate(npu_tasks);exp=75.0
    if abs(r-exp)<0.1:print(f"✅ Test 1 PASSED: npu_rate={r:.1f}%");p+=1
    else:print(f"❌ Test 1 FAILED: npu_rate={r:.1f}% (expected {exp}%)");f+=1
    s=speedup_ratio(t[t["npu_available"]==True]);exp_s=npu_tasks["cloud_time_ms"].mean()/npu_tasks["npu_time_ms"].mean()
    if abs(s-exp_s)<0.5:print(f"✅ Test 2 PASSED: speedup={s:.1f}x");p+=1
    else:print(f"❌ Test 2 FAILED: speedup={s:.1f}x (expected {exp_s:.1f}x)");f+=1
    u=count_unavailable(t);exp=1
    if u==exp:print(f"✅ Test 3 PASSED: unavailable={u}");p+=1
    else:print(f"❌ Test 3 FAILED: unavailable={u} (expected {exp})");f+=1
    print(f"\n{'🎉 All 3 tests passed!' if f==0 else f'🔧 {f} test(s) failed!'}")

if __name__=="__main__":
    print("🧪 Running self-tests…\n");run_tests()
