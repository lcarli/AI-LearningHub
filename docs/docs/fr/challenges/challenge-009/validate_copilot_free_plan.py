import subprocess
import sys

result = subprocess.run([sys.executable, "-m", "unittest", "test_copilot_free_plan.py"])
if result.returncode:
    raise SystemExit("Validation failed.")
print("CH009-FREE2026")
