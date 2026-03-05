#!/usr/bin/env python3
"""Bug-fix: Broken Research Analyzer - Lab 079."""
import io, pandas as pd
def total_sources_cited(trace):
    return trace["sources_found"].sum()
def writer_token_usage(trace):
    return trace["tokens_used"].mean()
def avg_quality(trace):
    return trace["quality_score"].min()
def run_tests():
    csv="step_id,agent,tokens_used,sources_found,sources_cited,quality_score\nS1,Planner,280,0,0,0.95\nS2,Researcher,0,12,0,0.90\nS3,Writer,1200,0,5,0.92\nS4,Reviewer,600,0,5,0.88"
    t=pd.read_csv(io.StringIO(csv));p,f=0,0
    s=total_sources_cited(t);exp=10
    if s==exp:print(f"OK T1: {s}");p+=1
    else:print(f"FAIL T1: {s} (exp {exp})");f+=1
    w=writer_token_usage(t);exp=1200.0
    if abs(w-exp)<1:print(f"OK T2: {w:.0f}");p+=1
    else:print(f"FAIL T2: {w:.0f} (exp {exp:.0f})");f+=1
    a=avg_quality(t);exp=0.9125
    if abs(a-exp)<0.01:print(f"OK T3: {a:.3f}");p+=1
    else:print(f"FAIL T3: {a:.3f} (exp {exp:.3f})");f+=1
    print(f"\n{'All passed!' if f==0 else f'{f} failed'}")
if __name__=="__main__":print("Tests:\n");run_tests()
