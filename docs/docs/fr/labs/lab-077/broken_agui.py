#!/usr/bin/env python3
"""Bug-fix: Broken AG-UI Analyzer - Lab 077."""
import io, pandas as pd
def count_agent_events(events):
    return (events["direction"] == "frontend->agent").sum()
def count_state_events(events):
    return (events["event_type"] == "TextMessageContent").sum()
def bidirectional_count(events):
    return events["direction"].nunique()
def run_tests():
    csv="event_type,direction\nTextMessageStart,agent->frontend\nUserMessage,frontend->agent\nStateUpdate,agent->frontend\nStateDelta,agent->frontend\nUserAction,frontend->agent"
    e=pd.read_csv(io.StringIO(csv));p,f=0,0
    n=count_agent_events(e);exp=3
    if n==exp:print(f"OK T1: {n}");p+=1
    else:print(f"FAIL T1: {n} (exp {exp})");f+=1
    s=count_state_events(e);exp=2
    if s==exp:print(f"OK T2: {s}");p+=1
    else:print(f"FAIL T2: {s} (exp {exp})");f+=1
    b=bidirectional_count(e);exp=2
    if b==exp:print(f"OK T3: {b}");p+=1
    else:print(f"FAIL T3: {b} (exp {exp})");f+=1
    print(f"\n{'All passed!' if f==0 else f'{f} failed'}")
if __name__=="__main__":print("Tests:\n");run_tests()
