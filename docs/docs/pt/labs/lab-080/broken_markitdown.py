#!/usr/bin/env python3
"""Bug-fix: Broken MarkItDown Analyzer - Lab 080."""
import io, pandas as pd
def success_rate(results):
    return (results["conversion_success"] == False).mean() * 100
def avg_quality_successful(results):
    return results["quality_score"].mean()
def total_tables(results):
    return results["images_found"].sum()
def run_tests():
    csv="test_id,conversion_success,quality_score,tables_found,images_found\nD1,true,0.92,6,3\nD2,true,0.95,2,8\nD3,false,0.00,0,0\nD4,true,0.85,1,22"
    r=pd.read_csv(io.StringIO(csv));r["conversion_success"]=r["conversion_success"].astype(str).str.lower()=="true"
    p,f=0,0
    s=success_rate(r);exp=75.0
    if abs(s-exp)<0.1:print(f"OK T1: {s:.1f}%");p+=1
    else:print(f"FAIL T1: {s:.1f}% (exp {exp}%)");f+=1
    a=avg_quality_successful(r);exp=0.9067
    if abs(a-exp)<0.01:print(f"OK T2: {a:.3f}");p+=1
    else:print(f"FAIL T2: {a:.3f} (exp {exp:.3f})");f+=1
    t=total_tables(r);exp=9
    if t==exp:print(f"OK T3: {t}");p+=1
    else:print(f"FAIL T3: {t} (exp {exp})");f+=1
    print(f"\n{'All passed!' if f==0 else f'{f} failed'}")
if __name__=="__main__":print("Tests:\n");run_tests()
