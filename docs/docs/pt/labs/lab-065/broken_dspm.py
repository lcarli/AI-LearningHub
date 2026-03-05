#!/usr/bin/env python3
"""🐛 Broken DSPM Analyzer — Lab 065. Fix 3 bugs, run self-tests."""
import io, pandas as pd

def count_dlp_violations(interactions: pd.DataFrame) -> int:
    # 🐛 Bug #1: Counts audit_logged instead of dlp_violation
    return (interactions["audit_logged"] == True).sum()

def count_prompt_injections(interactions: pd.DataFrame) -> int:
    # 🐛 Bug #2: Counts contains_pii instead of prompt_injection_detected
    return (interactions["contains_pii"] == True).sum()

def critical_risk_percentage(interactions: pd.DataFrame) -> float:
    # 🐛 Bug #3: Counts 'high' instead of 'critical'
    crit = (interactions["risk_score"] == "high").sum()
    return crit / len(interactions) * 100

def run_tests():
    csv="""\
interaction_id,dlp_violation,prompt_injection_detected,contains_pii,audit_logged,risk_score
I1,false,false,false,true,low
I2,true,false,true,true,high
I3,false,true,false,true,critical
I4,true,true,true,true,critical
I5,false,false,false,true,low"""
    i=pd.read_csv(io.StringIO(csv))
    for c in ["dlp_violation","prompt_injection_detected","contains_pii","audit_logged"]:
        i[c]=i[c].astype(str).str.lower()=="true"
    p,f=0,0
    d=count_dlp_violations(i);exp=2
    if d==exp:print(f"✅ Test 1 PASSED: dlp_violations={d}");p+=1
    else:print(f"❌ Test 1 FAILED: dlp_violations={d} (expected {exp})");f+=1
    pi=count_prompt_injections(i);exp=2
    if pi==exp:print(f"✅ Test 2 PASSED: injections={pi}");p+=1
    else:print(f"❌ Test 2 FAILED: injections={pi} (expected {exp})");f+=1
    cr=critical_risk_percentage(i);exp=40.0
    if abs(cr-exp)<0.1:print(f"✅ Test 3 PASSED: critical={cr:.1f}%");p+=1
    else:print(f"❌ Test 3 FAILED: critical={cr:.1f}% (expected {exp}%)");f+=1
    print(f"\n{'🎉 All 3 tests passed!' if f==0 else f'🔧 {f} test(s) failed!'}")

if __name__=="__main__":
    print("🧪 Running self-tests…\n");run_tests()
