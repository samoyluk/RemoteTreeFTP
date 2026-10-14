"""Run isolated regression scenarios without installing Sublime or dependencies."""
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
files = sorted((ROOT / "tests").glob("test_*.py"))
for test in files:
    subprocess.run([sys.executable, str(test)], cwd=str(ROOT), env=env, check=True)
print("Passed {} regression scenarios".format(len(files)))
