#!/usr/bin/env python3
"""Bug-fix: Broken GraphRAG Analyzer - Lab 067. Fix 3 bugs."""
import io, pandas as pd
def count_communities(graph):
    # Bug #1: Counts unique entity_type instead of community_id
    return graph["entity_type"].nunique()
def top_entity(graph):
    # Bug #2: Returns entity with LOWEST importance instead of highest
    return graph.loc[graph["importance_score"].idxmin(), "entity_name"]
def avg_connections(graph):
    # Bug #3: Returns max connections instead of mean
    return graph["connections"].max()
def run_tests():
    csv="entity_id,entity_name,entity_type,community_id,importance_score,connections\nE1,Tent,Product,C1,0.95,8\nE2,Boot,Product,C2,0.78,5\nE3,Policy,Policy,C3,0.88,7\nE4,Warehouse,Location,C3,0.65,4"
    g=pd.read_csv(io.StringIO(csv));p,f=0,0
    n=count_communities(g);exp=3
    if n==exp:print(f"OK T1: {n}");p+=1
    else:print(f"FAIL T1: {n} (exp {exp})");f+=1
    t=top_entity(g);exp="Tent"
    if t==exp:print(f"OK T2: {t}");p+=1
    else:print(f"FAIL T2: {t} (exp {exp})");f+=1
    a=avg_connections(g);exp=6.0
    if abs(a-exp)<0.1:print(f"OK T3: {a}");p+=1
    else:print(f"FAIL T3: {a} (exp {exp})");f+=1
    print(f"\n{'All passed!' if f==0 else f'{f} failed'}")
if __name__=="__main__":
    print("Tests:\n");run_tests()
