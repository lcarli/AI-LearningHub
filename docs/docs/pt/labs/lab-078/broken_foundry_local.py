#!/usr/bin/env python3
"""Bug-fix: Broken Foundry Local Analyzer - Lab 078."""
import io, pandas as pd
def smallest_model(models):
    return models.loc[models["parameters"].idxmax(), "model_alias"]
def cpu_only_models(models):
    return len(models[models["hardware_required"].str.contains("GPU")])
def avg_quality(models):
    models["quality_num"] = models["quality_vs_cloud"].str.rstrip("% of GPT-3.5").str.rstrip("% of GPT-4o-mini").str.rstrip("% of o3-mini").str.strip().astype(float)
    return models["quality_num"].max()
def run_tests():
    csv='model_alias,model_name,size_gb,parameters,hardware_required,quality_vs_cloud\nA,ModelA,2.0,3B,"CPU (8GB)",80% of GPT-3.5\nB,ModelB,8.0,14B,"GPU recommended",90% of GPT-4o-mini\nC,ModelC,0.4,0.5B,"CPU (4GB)",60% of GPT-3.5'
    m=pd.read_csv(io.StringIO(csv));p,f=0,0
    s=smallest_model(m);exp="C"
    if s==exp:print(f"OK T1: {s}");p+=1
    else:print(f"FAIL T1: {s} (exp {exp})");f+=1
    c=cpu_only_models(m);exp=2
    if c==exp:print(f"OK T2: {c}");p+=1
    else:print(f"FAIL T2: {c} (exp {exp})");f+=1
    a=avg_quality(m);exp=76.67
    if abs(a-exp)<1:print(f"OK T3: {a:.1f}");p+=1
    else:print(f"FAIL T3: {a:.1f} (exp {exp:.1f})");f+=1
    print(f"\n{'All passed!' if f==0 else f'{f} failed'}")
if __name__=="__main__":print("Tests:\n");run_tests()
