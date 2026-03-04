#!/usr/bin/env python3
"""Bug-fix: Broken Cache Analyzer - Lab 071. Fix 3 bugs."""
import io, pandas as pd
def avg_ttft_cached(bench):
    # Bug #1: Averages miss TTFT instead of hit TTFT
    return bench[bench["cache_status"]=="miss"]["ttft_ms"].mean()
def total_cost_savings(bench):
    # Bug #2: Subtracts cached_cost from input_cost (should sum miss input costs - sum hit cached costs)
    return bench["input_cost_usd"].sum() - bench["cached_cost_usd"].sum()
def cache_hit_rate(bench):
    # Bug #3: Counts misses / total instead of hits / total
    return (bench["cache_status"]=="miss").sum() / len(bench) * 100
def run_tests():
    csv="request_id,cache_status,ttft_ms,input_cost_usd,cached_cost_usd\nR1,miss,2800,0.45,0.00\nR2,hit,180,0.00,0.05\nR3,hit,175,0.00,0.05\nR4,miss,2750,0.45,0.00"
    b=pd.read_csv(io.StringIO(csv));p,f=0,0
    t=avg_ttft_cached(b);exp=177.5
    if abs(t-exp)<1:print(f"OK T1: {t}");p+=1
    else:print(f"FAIL T1: {t} (exp {exp})");f+=1
    s=total_cost_savings(b);exp=0.80
    if abs(s-exp)<0.01:print(f"OK T2: {s}");p+=1
    else:print(f"FAIL T2: {s} (exp {exp})");f+=1
    r=cache_hit_rate(b);exp=50.0
    if abs(r-exp)<0.1:print(f"OK T3: {r}");p+=1
    else:print(f"FAIL T3: {r} (exp {exp})");f+=1
    print(f"\n{'All passed!' if f==0 else f'{f} failed'}")
if __name__=="__main__":
    print("Tests:\n");run_tests()
