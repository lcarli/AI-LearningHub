#!/usr/bin/env python3
"""Bug-fix: Broken Manifest Parser - Lab 069. Fix 3 bugs."""
import json
def count_knowledge_sources(manifest):
    # Bug #1: Counts api_plugins instead of knowledge_sources
    return len(manifest["api_plugins"])
def has_web_search(manifest):
    # Bug #2: Checks code_interpreter instead of web_search
    return manifest["capabilities"]["code_interpreter"]
def get_data_classification(manifest):
    # Bug #3: Returns available_to instead of data_classification
    return manifest["admin_settings"]["available_to"]
def run_tests():
    m={"knowledge_sources":[{"type":"sp"},{"type":"gc"},{"type":"gc"}],"api_plugins":[{"name":"inv"}],"capabilities":{"web_search":False,"code_interpreter":False},"admin_settings":{"available_to":"org","data_classification":"confidential"}}
    p,f=0,0
    n=count_knowledge_sources(m);exp=3
    if n==exp:print(f"OK T1: {n}");p+=1
    else:print(f"FAIL T1: {n} (exp {exp})");f+=1
    w=has_web_search(m);exp=False
    if w==exp:print(f"OK T2: {w}");p+=1
    else:print(f"FAIL T2: {w} (exp {exp})");f+=1
    d=get_data_classification(m);exp="confidential"
    if d==exp:print(f"OK T3: {d}");p+=1
    else:print(f"FAIL T3: {d} (exp {exp})");f+=1
    print(f"\n{'All passed!' if f==0 else f'{f} failed'}")
if __name__=="__main__":
    print("Tests:\n");run_tests()
