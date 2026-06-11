
import os
import sys
import traceback
from pathlib import Path

# Set up logging to a file
log_file = Path(__file__).parent / "server_log.txt"
log_file.write_text("")  # Clear existing log

def log(message):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(message + "\n")
    print(message)

try:
    src_dir = Path(__file__).parent / "src"
    os.chdir(src_dir)
    sys.path.insert(0, str(src_dir))
    log(f"Changed directory to: {src_dir}")
    log(f"Python path: {sys.path}")
    
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    log("Set DJANGO_SETTINGS_MODULE")
    
    from django.core.management import execute_from_command_line
    log("Imported Django management")
    
    log("Starting Django server...")
    execute_from_command_line(["manage.py", "runserver", "127.0.0.1:8000", "--noreload"])
except Exception as e:
    log(f"ERROR: {str(e)}")
    log("Traceback:")
    log(traceback.format_exc())
