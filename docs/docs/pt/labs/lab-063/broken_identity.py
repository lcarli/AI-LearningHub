#!/usr/bin/env python3
"""🐛 Broken Identity Analyzer — Lab 063. Fix 3 bugs, run self-tests."""
import io, pandas as pd

def count_violations(scenarios: pd.DataFrame) -> int:
    # 🐛 Bug #1: Counts compliant=True instead of compliant=False
    return (scenarios["compliant"] == True).sum()

def count_critical_risks(scenarios: pd.DataFrame) -> int:
    # 🐛 Bug #2: Counts 'high' instead of 'critical'
    return (scenarios["risk_level"] == "high").sum()

def obo_percentage(scenarios: pd.DataFrame) -> float:
    # 🐛 Bug #3: Counts client_credentials instead of OBO
    obo = (scenarios["identity_flow"] == "client_credentials").sum()
    return obo / len(scenarios) * 100

def run_tests():
    csv="""\
scenario_id,permission_type,identity_flow,risk_level,compliant
S1,delegated,OBO,low,true
S2,delegated,OBO,medium,true
S3,application,client_credentials,high,false
S4,delegated,OBO,low,true
S5,application,client_credentials,critical,false"""
    s=pd.read_csv(io.StringIO(csv))
    s["compliant"]=s["compliant"].astype(str).str.lower()=="true"
    p,f=0,0
    v=count_violations(s);exp=2
    if v==exp:print(f"✅ Test 1 PASSED: violations={v}");p+=1
    else:print(f"❌ Test 1 FAILED: violations={v} (expected {exp})");f+=1
    c=count_critical_risks(s);exp=1
    if c==exp:print(f"✅ Test 2 PASSED: critical={c}");p+=1
    else:print(f"❌ Test 2 FAILED: critical={c} (expected {exp})");f+=1
    o=obo_percentage(s);exp=60.0
    if abs(o-exp)<0.1:print(f"✅ Test 3 PASSED: obo={o:.1f}%");p+=1
    else:print(f"❌ Test 3 FAILED: obo={o:.1f}% (expected {exp}%)");f+=1
    print(f"\n{'🎉 All 3 tests passed!' if f==0 else f'🔧 {f} test(s) failed!'}")

if __name__=="__main__":
    print("🧪 Running self-tests…\n");run_tests()
