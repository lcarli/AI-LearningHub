#!/usr/bin/env python3
"""🐛 Broken Voice Analyzer — Lab 059. Fix 3 bugs, run self-tests."""
import io, pandas as pd

def calculate_p95_latency(sessions: pd.DataFrame) -> float:
    # 🐛 Bug #1: Calculates mean of latency_p95_ms instead of the actual P95
    #   (should use .quantile(0.95) on latency_p50_ms, or just mean the p95 column)
    #   Actually the bug is: uses latency_p50_ms average instead of latency_p95_ms average
    return sessions["latency_p50_ms"].mean()

def count_negative_sessions(sessions: pd.DataFrame) -> int:
    # 🐛 Bug #2: Counts 'neutral' instead of 'negative'
    return (sessions["sentiment"] == "neutral").sum()

def rag_usage_rate(sessions: pd.DataFrame) -> float:
    # 🐛 Bug #3: Divides by rag_used count instead of total sessions
    rag = sessions[sessions["rag_used"] == True]
    return len(rag) / len(rag) * 100

def run_tests():
    csv="""\
session_id,latency_p50_ms,latency_p95_ms,sentiment,rag_used
S1,85,170,positive,true
S2,92,185,neutral,true
S3,88,195,negative,true
S4,75,150,positive,false
S5,95,210,negative,false"""
    s=pd.read_csv(io.StringIO(csv));s["rag_used"]=s["rag_used"].astype(str).str.lower()=="true"
    p,f=0,0
    lat=calculate_p95_latency(s);exp=182.0  # mean of p95 column
    if abs(lat-exp)<1:print(f"✅ Test 1 PASSED: avg_p95={lat:.0f}ms");p+=1
    else:print(f"❌ Test 1 FAILED: avg_p95={lat:.0f}ms (expected {exp:.0f}ms)");f+=1
    n=count_negative_sessions(s);exp=2
    if n==exp:print(f"✅ Test 2 PASSED: negative={n}");p+=1
    else:print(f"❌ Test 2 FAILED: negative={n} (expected {exp})");f+=1
    r=rag_usage_rate(s);exp=60.0  # 3/5
    if abs(r-exp)<0.1:print(f"✅ Test 3 PASSED: rag_rate={r:.1f}%");p+=1
    else:print(f"❌ Test 3 FAILED: rag_rate={r:.1f}% (expected {exp:.1f}%)");f+=1
    print(f"\n{'🎉 All 3 tests passed!' if f==0 else f'🔧 {f} test(s) failed!'}")

if __name__=="__main__":
    print("🧪 Running self-tests…\n");run_tests()
