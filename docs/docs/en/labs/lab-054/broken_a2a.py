#!/usr/bin/env python3
"""🐛 Broken A2A Parser — Lab 054. Fix 3 bugs, run self-tests."""
import json, io

def count_total_skills(cards: list) -> int:
    # 🐛 Bug #1: Only counts skills in the FIRST card
    return len(cards[0]["skills"])

def count_push_enabled(cards: list) -> int:
    # 🐛 Bug #2: Checks 'streaming' instead of 'pushNotifications'
    return sum(1 for c in cards if c["capabilities"]["streaming"])

def get_auth_types(cards: list) -> list:
    # 🐛 Bug #3: Returns 'required' field (bool) instead of 'type' field
    return [c["authentication"]["required"] for c in cards]

def run_tests():
    cards = [
        {"name":"A","skills":[{"id":"s1"},{"id":"s2"}],"capabilities":{"streaming":True,"pushNotifications":False},"authentication":{"type":"bearer","required":True}},
        {"name":"B","skills":[{"id":"s3"},{"id":"s4"},{"id":"s5"}],"capabilities":{"streaming":False,"pushNotifications":True},"authentication":{"type":"oauth2","required":True}},
    ]
    p,f=0,0
    s=count_total_skills(cards);exp=5
    if s==exp:print(f"✅ Test 1 PASSED: skills={s}");p+=1
    else:print(f"❌ Test 1 FAILED: skills={s} (expected {exp})");f+=1
    n=count_push_enabled(cards);exp=1
    if n==exp:print(f"✅ Test 2 PASSED: push={n}");p+=1
    else:print(f"❌ Test 2 FAILED: push={n} (expected {exp})");f+=1
    t=get_auth_types(cards);exp=["bearer","oauth2"]
    if t==exp:print(f"✅ Test 3 PASSED: types={t}");p+=1
    else:print(f"❌ Test 3 FAILED: types={t} (expected {exp})");f+=1
    print(f"\n{'🎉 All 3 tests passed!' if f==0 else f'🔧 {f} test(s) failed — keep debugging!'}")

if __name__=="__main__":
    print("🧪 Running self-tests…\n");run_tests()
