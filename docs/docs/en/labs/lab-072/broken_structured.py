#!/usr/bin/env python3
"""Bug-fix: Broken Structured Output Analyzer - Lab 072. Fix 3 bugs."""
import io, pandas as pd
def schema_success_rate(df):
    # Bug #1: Counts json_parse_success instead of structured_output_valid
    schema=df[df["model"]=="gpt-4o"]
    return schema["json_parse_success"].mean() * 100
def no_schema_accuracy(df):
    # Bug #2: Uses field_accuracy from schema model instead of no-schema
    no_schema=df[df["model"]=="gpt-4o"]
    return no_schema["field_accuracy_pct"].mean()
def avg_tokens(df, model):
    # Bug #3: Doesn't filter by model
    return df["tokens"].mean()
def run_tests():
    csv="test_id,model,structured_output_valid,json_parse_success,field_accuracy_pct,tokens\nT1,gpt-4o,true,true,100,120\nT2,gpt-4o,true,true,95,115\nT3,gpt-4o-no-schema,false,true,75,160\nT4,gpt-4o-no-schema,false,false,55,95"
    df=pd.read_csv(io.StringIO(csv))
    for c in ["structured_output_valid","json_parse_success"]:df[c]=df[c].astype(str).str.lower()=="true"
    p,f=0,0
    r=schema_success_rate(df);exp=100.0
    if abs(r-exp)<0.1:print(f"OK T1: {r}");p+=1
    else:print(f"FAIL T1: {r} (exp {exp})");f+=1
    a=no_schema_accuracy(df);exp=65.0
    if abs(a-exp)<0.1:print(f"OK T2: {a}");p+=1
    else:print(f"FAIL T2: {a} (exp {exp})");f+=1
    t=avg_tokens(df,"gpt-4o");exp=117.5
    if abs(t-exp)<0.1:print(f"OK T3: {t}");p+=1
    else:print(f"FAIL T3: {t} (exp {exp})");f+=1
    print(f"\n{'All passed!' if f==0 else f'{f} failed'}")
if __name__=="__main__":
    print("Tests:\n");run_tests()
