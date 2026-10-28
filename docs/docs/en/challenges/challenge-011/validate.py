import subprocess
import sys

result = subprocess.run([sys.executable, '-m', 'unittest', '-v'])
if result.returncode:
    raise SystemExit('Validation failed.')
print('CH011-EVALRAG')
