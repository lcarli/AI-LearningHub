#!/usr/bin/env python3
"""🐛 Broken Connector Analyzer — Lab 056. Fix 3 bugs, run self-tests."""
import io, pandas as pd

def avg_freshness_by_type(df: pd.DataFrame) -> dict:
    # 🐛 Bug #1: Returns latency_ms instead of data_freshness_sec
    return df.groupby("connector_type")["latency_ms"].mean().to_dict()

def count_non_compliant(df: pd.DataFrame) -> int:
    # 🐛 Bug #2: Counts compliant=True instead of compliant=False
    return (df["compliant"] == True).sum()

def latency_ratio(df: pd.DataFrame) -> float:
    # 🐛 Bug #3: Divides synced/federated instead of federated/synced
    fed = df[df["connector_type"]=="federated"]["latency_ms"].mean()
    syn = df[df["connector_type"]=="synced"]["latency_ms"].mean()
    return syn / fed

def run_tests():
    csv = """\
query_id,connector_type,latency_ms,data_freshness_sec,compliant
Q1,federated,400,0,true
Q2,synced,100,3600,true
Q3,federated,500,0,true
Q4,synced,120,1800,false"""
    df=pd.read_csv(io.StringIO(csv));p,f=0,0
    # Test 1: avg freshness: federated=0, synced=2700
    r=avg_freshness_by_type(df);exp_f=0.0;exp_s=2700.0
    if abs(r.get("federated",999)-exp_f)<1 and abs(r.get("synced",999)-exp_s)<1:
        print(f"✅ Test 1 PASSED: {r}");p+=1
    else:print(f"❌ Test 1 FAILED: {r} (expected fed=0, syn=2700)");f+=1
    # Test 2: non-compliant = 1
    n=count_non_compliant(df);exp=1
    if n==exp:print(f"✅ Test 2 PASSED: non_compliant={n}");p+=1
    else:print(f"❌ Test 2 FAILED: non_compliant={n} (expected {exp})");f+=1
    # Test 3: ratio = federated/synced = 450/110 ≈ 4.09
    ratio=latency_ratio(df);exp=450/110
    if abs(ratio-exp)<0.1:print(f"✅ Test 3 PASSED: ratio={ratio:.2f}");p+=1
    else:print(f"❌ Test 3 FAILED: ratio={ratio:.2f} (expected {exp:.2f})");f+=1
    print(f"\n{'🎉 All 3 tests passed!' if f==0 else f'🔧 {f} test(s) failed!'}")

if __name__=="__main__":
    print("🧪 Running self-tests…\n");run_tests()
