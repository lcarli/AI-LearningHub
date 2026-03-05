#!/usr/bin/env python3
"""Bug-fix: Broken UX Analyzer - Lab 070. Fix 3 bugs."""
import io, pandas as pd
def top_pattern(patterns):
    # Bug #1: Returns pattern with LOWEST satisfaction
    return patterns.loc[patterns["user_satisfaction"].idxmin(), "pattern_name"]
def count_high_complexity(patterns):
    # Bug #2: Counts 'low' instead of 'high'
    return (patterns["complexity"] == "low").sum()
def avg_accessibility(patterns, category):
    # Bug #3: Doesn't filter by category
    return patterns["accessibility_score"].mean()
def run_tests():
    csv="pattern_id,pattern_name,category,complexity,user_satisfaction,accessibility_score\nP1,Card,interactive,medium,4.5,90\nP2,Text,basic,low,3.2,95\nP3,Form,interactive,high,4.1,80"
    p_df=pd.read_csv(io.StringIO(csv));p,f=0,0
    t=top_pattern(p_df);exp="Card"
    if t==exp:print(f"OK T1: {t}");p+=1
    else:print(f"FAIL T1: {t} (exp {exp})");f+=1
    h=count_high_complexity(p_df);exp=1
    if h==exp:print(f"OK T2: {h}");p+=1
    else:print(f"FAIL T2: {h} (exp {exp})");f+=1
    a=avg_accessibility(p_df,"interactive");exp=85.0
    if abs(a-exp)<0.1:print(f"OK T3: {a}");p+=1
    else:print(f"FAIL T3: {a} (exp {exp})");f+=1
    print(f"\n{'All passed!' if f==0 else f'{f} failed'}")
if __name__=="__main__":
    print("Tests:\n");run_tests()
