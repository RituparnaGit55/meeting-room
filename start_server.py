import os
import sys
from pathlib import Path

# Set up paths
project_dir = Path(__file__).parent
src_dir = project_dir / "src"
os.chdir(src_dir)
sys.path.insert(0, str(src_dir))

# Set Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

import django
django.setup()

from django.core.management import execute_from_command_line

print("Starting MeetFlow server...")
print("Open http://127.0.0.1:8001 in your browser!")
execute_from_command_line(["manage.py", "runserver", "127.0.0.1:8001"])
