#!/usr/bin/env python3
"""Bug-fix: Broken Search Analyzer - Lab 068. Fix 3 bugs."""
import io, pandas as pd
def avg_recall_by_strategy(df, strategy):
    # Bug #1: Returns precision instead of recall
    sub = df[df["search_strategy"] == strategy]
    return sub["precision"].mean()
def best_strategy(df):
    # Bug #2: Finds strategy with lowest recall instead of highest
    return df.groupby("search_strategy")["recall"].mean().idxmin()
def reranker_improvement(df):
    # Bug #3: Compares bm25 to hybrid instead of hybrid to hybrid+rerank
    bm25 = df[df["search_strategy"]=="bm25"]["recall"].mean()
    hybrid = df[df["search_strategy"]=="hybrid_rrf"]["recall"].mean()
    return hybrid - bm25
def run_tests():
    csv="query_id,search_strategy,recall,precision,reranker_used\nQ1,bm25,0.50,0.20,false\nQ2,vector,0.70,0.60,false\nQ3,hybrid_rrf,0.85,0.50,false\nQ4,hybrid_rrf,0.95,0.55,true"
    df=pd.read_csv(io.StringIO(csv));p,f=0,0
    r=avg_recall_by_strategy(df,"bm25");exp=0.50
    if abs(r-exp)<0.01:print(f"OK T1: {r}");p+=1
    else:print(f"FAIL T1: {r} (exp {exp})");f+=1
    b=best_strategy(df);exp="hybrid_rrf"
    if b==exp:print(f"OK T2: {b}");p+=1
    else:print(f"FAIL T2: {b} (exp {exp})");f+=1
    i=reranker_improvement(df);exp=0.05
    if abs(i-exp)<0.01:print(f"OK T3: {i}");p+=1
    else:print(f"FAIL T3: {i} (exp {exp})");f+=1
    print(f"\n{'All passed!' if f==0 else f'{f} failed'}")
if __name__=="__main__":
    print("Tests:\n");run_tests()
