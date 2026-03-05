#!/usr/bin/env python3
"""🐛 Broken APIM Analyzer — Lab 064. Fix 3 bugs, run self-tests."""
import io, pandas as pd

def count_non_compliant(servers: pd.DataFrame) -> int:
    # 🐛 Bug #1: Counts compliant=True instead of False
    return (servers["compliant"] == True).sum()

def total_monthly_calls(servers: pd.DataFrame) -> int:
    # 🐛 Bug #2: Returns average instead of sum
    return int(servers["monthly_calls"].mean())

def servers_without_oauth(servers: pd.DataFrame) -> list:
    # 🐛 Bug #3: Filters auth_type == 'oauth2' (finds OAuth servers, not non-OAuth)
    non_oauth = servers[servers["auth_type"] == "oauth2"]
    return non_oauth["server_name"].tolist()

def run_tests():
    csv="""\
server_id,server_name,auth_type,has_dlp,has_logging,monthly_calls,compliant
S1,product-api,oauth2,true,true,10000,true
S2,legacy-erp,basic,false,false,5000,false
S3,analytics,api_key,false,true,8000,false
S4,hr-system,oauth2,true,true,3000,true"""
    s=pd.read_csv(io.StringIO(csv))
    s["compliant"]=s["compliant"].astype(str).str.lower()=="true"
    p,f=0,0
    n=count_non_compliant(s);exp=2
    if n==exp:print(f"✅ Test 1 PASSED: non_compliant={n}");p+=1
    else:print(f"❌ Test 1 FAILED: non_compliant={n} (expected {exp})");f+=1
    t=total_monthly_calls(s);exp=26000
    if t==exp:print(f"✅ Test 2 PASSED: total_calls={t:,}");p+=1
    else:print(f"❌ Test 2 FAILED: total_calls={t:,} (expected {exp:,})");f+=1
    w=servers_without_oauth(s);exp=["legacy-erp","analytics"]
    if sorted(w)==sorted(exp):print(f"✅ Test 3 PASSED: non_oauth={w}");p+=1
    else:print(f"❌ Test 3 FAILED: non_oauth={w} (expected {exp})");f+=1
    print(f"\n{'🎉 All 3 tests passed!' if f==0 else f'🔧 {f} test(s) failed!'}")

if __name__=="__main__":
    print("🧪 Running self-tests…\n");run_tests()
