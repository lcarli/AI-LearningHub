#!/usr/bin/env python3
"""🐛 Broken Reasoning Analyzer — Lab 060. Fix 3 bugs, run self-tests."""
import io, pandas as pd

def model_accuracy(bench: pd.DataFrame, model: str) -> float:
    # 🐛 Bug #1: Sums time column instead of correct column
    col = f"{model}_time_sec"
    return bench[col].mean() * 100

def fastest_model(bench: pd.DataFrame) -> str:
    # 🐛 Bug #2: Returns model with HIGHEST avg time (slowest) instead of lowest
    models = {"gpt4o": bench["gpt4o_time_sec"].mean(),
              "o3": bench["o3_time_sec"].mean(),
              "deepseek_r1": bench["deepseek_r1_time_sec"].mean()}
    return max(models, key=models.get)

def hard_problem_accuracy(bench: pd.DataFrame, model: str) -> float:
    # 🐛 Bug #3: Filters 'easy' instead of 'hard'
    hard = bench[bench["difficulty"] == "easy"]
    col = f"{model}_correct"
    return hard[col].mean() * 100

def run_tests():
    csv="""\
problem_id,category,difficulty,gpt4o_correct,gpt4o_time_sec,o3_correct,o3_time_sec,deepseek_r1_correct,deepseek_r1_time_sec
P1,math,easy,true,1.0,true,3.0,true,2.5
P2,math,hard,false,2.0,true,8.0,true,6.0
P3,code,easy,true,1.5,true,4.0,true,3.0
P4,code,hard,false,3.0,true,10.0,false,8.0"""
    b=pd.read_csv(io.StringIO(csv))
    for m in ["gpt4o","o3","deepseek_r1"]:
        b[f"{m}_correct"]=b[f"{m}_correct"].astype(str).str.lower()=="true"
    p,f=0,0
    a=model_accuracy(b,"gpt4o");exp=50.0  # 2/4
    if abs(a-exp)<0.1:print(f"✅ Test 1 PASSED: gpt4o_acc={a:.1f}%");p+=1
    else:print(f"❌ Test 1 FAILED: gpt4o_acc={a:.1f}% (expected {exp}%)");f+=1
    fm=fastest_model(b);exp="gpt4o"  # lowest avg time
    if fm==exp:print(f"✅ Test 2 PASSED: fastest={fm}");p+=1
    else:print(f"❌ Test 2 FAILED: fastest={fm} (expected {exp})");f+=1
    h=hard_problem_accuracy(b,"o3");exp=100.0  # o3 gets both hard right
    if abs(h-exp)<0.1:print(f"✅ Test 3 PASSED: o3_hard={h:.1f}%");p+=1
    else:print(f"❌ Test 3 FAILED: o3_hard={h:.1f}% (expected {exp}%)");f+=1
    print(f"\n{'🎉 All 3 tests passed!' if f==0 else f'🔧 {f} test(s) failed!'}")

if __name__=="__main__":
    print("🧪 Running self-tests…\n");run_tests()
