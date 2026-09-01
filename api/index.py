import os
import sys
import shutil
from pathlib import Path

# Add src folder to Python path for Django import resolution
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

# Determine writable directory for SQLite on serverless environments
if os.name == "nt":
    temp_dir = Path(os.environ.get("TEMP", os.environ.get("TMP", BASE_DIR / "scratch")))
else:
    temp_dir = Path("/tmp")

temp_dir.mkdir(parents=True, exist_ok=True)
tmp_db = temp_dir / "db.sqlite3"
src_db = SRC_DIR / "db.sqlite3"

if src_db.exists() and not tmp_db.exists():
    try:
        shutil.copy2(src_db, tmp_db)
    except Exception as err:
        print("Failed to copy seed db to temp dir:", err)

import django
django.setup()

# Auto-apply migrations if running on serverless
try:
    from django.core.management import call_command
    call_command("migrate", interactive=False)
except Exception as err:
    print("Migration status/notice:", err)

from config.wsgi import application

# Vercel serverless entry point
app = application
