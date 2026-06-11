
import os
import sys
from pathlib import Path

src_dir = Path(__file__).parent / "src"
os.chdir(src_dir)
sys.path.insert(0, str(src_dir))  # Add src to Python path
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

try:
    from django.core.management import execute_from_command_line
    print("Starting Django server...")
    execute_from_command_line(["manage.py", "runserver", "0.0.0.0:8000", "--noreload"])
except Exception as e:
    print("Error starting server:", str(e))
    import traceback
    print(traceback.format_exc())
    input("Press Enter to exit...")
