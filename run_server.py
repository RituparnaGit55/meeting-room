
import os
import sys
from pathlib import Path

src_dir = Path(__file__).parent / "src"
os.chdir(src_dir)
sys.path.insert(0, str(src_dir))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

try:
    from django.core.management import execute_from_command_line
    print("Starting Django server at http://127.0.0.1:8000/")
    execute_from_command_line(["manage.py", "runserver", "--noreload"])
except Exception as e:
    print("Error starting server:", str(e))
    import traceback
    print(traceback.format_exc())
