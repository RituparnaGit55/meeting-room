
import os
import sys
import subprocess

os.chdir(os.path.join(os.path.dirname(__file__), "src"))

try:
    result = subprocess.run(
        [sys.executable, "manage.py", "runserver", "--noreload"],
        capture_output=True,
        text=True,
        timeout=10
    )
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    print("Exit code:", result.returncode)
except Exception as e:
    print("Error:", str(e))
    import traceback
    print(traceback.format_exc())
