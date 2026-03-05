#!/usr/bin/env python3
"""Bug-fix: Broken Multi-Modal RAG Analyzer - Lab 083."""
import io, pandas as pd
def multimodal_improvement(chunks):
    text = chunks[chunks["has_image"]==False]["retrieval_score_text_only"].mean()
    mm = chunks[chunks["has_image"]==True]["retrieval_score_multimodal"].mean()
    return mm - text
def image_chunk_count(chunks):
    return (chunks["has_table"]==True).sum()
def avg_multimodal_score(chunks):
    return chunks["retrieval_score_text_only"].mean()
def run_tests():
    csv="chunk_id,has_image,has_table,retrieval_score_text_only,retrieval_score_multimodal\nC1,false,false,0.85,0.85\nC2,false,true,0.72,0.88\nC3,true,false,0.15,0.82\nC4,true,false,0.10,0.91"
    c=pd.read_csv(io.StringIO(csv))
    c["has_image"]=c["has_image"].astype(str).str.lower()=="true"
    c["has_table"]=c["has_table"].astype(str).str.lower()=="true"
    p,f=0,0
    i=multimodal_improvement(c);exp=0.865-0.785
    if abs(i-exp)<0.02:print(f"OK T1: {i:.3f}");p+=1
    else:print(f"FAIL T1: {i:.3f} (exp {exp:.3f})");f+=1
    ic=image_chunk_count(c);exp=2
    if ic==exp:print(f"OK T2: {ic}");p+=1
    else:print(f"FAIL T2: {ic} (exp {exp})");f+=1
    a=avg_multimodal_score(c);exp=0.865
    if abs(a-exp)<0.01:print(f"OK T3: {a:.3f}");p+=1
    else:print(f"FAIL T3: {a:.3f} (exp {exp:.3f})");f+=1
    print(f"\n{'All passed!' if f==0 else f'{f} failed'}")
if __name__=="__main__":print("Tests:\n");run_tests()
