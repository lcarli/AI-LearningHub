#!/usr/bin/env python3
"""Bug-fix: Broken Migration Analyzer - Lab 076."""
import io, pandas as pd
def count_low_effort(matrix):
    return (matrix["migration_effort"] == "high").sum()
def features_in_maf_only(matrix):
    return len(matrix[matrix["semantic_kernel"] == "not supported"])
def migration_coverage(matrix):
    return matrix["agent_framework"].nunique() / len(matrix) * 100
def run_tests():
    csv="feature,semantic_kernel,agent_framework,migration_effort\nPlugins,KernelPlugin,AgentSkills,medium\nA2A,not supported,native A2A,n/a\nStreaming,IAsyncEnumerable,built-in,low\nDevUI,not available,DevUI,low"
    m=pd.read_csv(io.StringIO(csv));p,f=0,0
    n=count_low_effort(m);exp=2
    if n==exp:print(f"OK T1: {n}");p+=1
    else:print(f"FAIL T1: {n} (exp {exp})");f+=1
    a=features_in_maf_only(m);exp=1
    if a==exp:print(f"OK T2: {a}");p+=1
    else:print(f"FAIL T2: {a} (exp {exp})");f+=1
    c=migration_coverage(m);exp=100.0
    if abs(c-exp)<0.1:print(f"OK T3: {c:.0f}%");p+=1
    else:print(f"FAIL T3: {c:.0f}% (exp {exp:.0f}%)");f+=1
    print(f"\n{'All passed!' if f==0 else f'{f} failed'}")
if __name__=="__main__":print("Tests:\n");run_tests()
