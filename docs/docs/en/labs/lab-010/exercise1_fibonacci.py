# exercise1_fibonacci.py
# 🐛 BUG HUNT — This file has 3 bugs. Can you find them all using Copilot /fix?
#
# TASK: The fibonacci() function should return a list of the first n
#       Fibonacci numbers: [0, 1, 1, 2, 3, 5, 8, 13, ...]
#
# EXPECTED OUTPUT (for n=8):
#   fibonacci(8)  → [0, 1, 1, 2, 3, 5, 8, 13]
#   fibonacci(1)  → [0]
#   fibonacci(0)  → []
#
# HOW TO USE THIS EXERCISE:
#   1. Open this file in VS Code
#   2. Select ALL the code (Ctrl+A)
#   3. Open Copilot Chat → type: /fix
#   4. Read Copilot's explanation of each bug
#   5. Accept the fix and run the tests below to verify

def fibonacci(n):
    """Return a list of the first n Fibonacci numbers."""
    if n = 0:           # BUG 1: syntax error
        return []
    
    sequence = [0, 1]
    
    for i in range(2, n):
        next_val = sequence[i-1] + sequence[i-2]
        sequence.append(next_val)
    
    return sequence[n]  # BUG 2: should return a slice, not a single element
                        # BUG 3: what happens when n=1? sequence has 2 elements but we only want 1


# --- Tests (run after fixing) ---
if __name__ == "__main__":
    assert fibonacci(0) == [], f"Expected [], got {fibonacci(0)}"
    assert fibonacci(1) == [0], f"Expected [0], got {fibonacci(1)}"
    assert fibonacci(8) == [0, 1, 1, 2, 3, 5, 8, 13], f"Got {fibonacci(8)}"
    print("✅ All tests passed!")
