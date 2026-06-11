
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

print("Running Django system check...")
execute_from_command_line(["manage.py", "check"])
