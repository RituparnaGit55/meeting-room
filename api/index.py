import os
import sys
import shutil
from pathlib import Path

# Add src folder to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

# Copy seed database to writable temp folder on serverless startup if missing
if os.name == "nt":
    temp_dir = Path(os.environ.get("TEMP", os.environ.get("TMP", BASE_DIR / "scratch")))
else:
    temp_dir = Path("/tmp")

try:
    temp_dir.mkdir(parents=True, exist_ok=True)
    tmp_db = temp_dir / "db.sqlite3"
    src_db = SRC_DIR / "db.sqlite3"

    if src_db.exists() and not tmp_db.exists():
        shutil.copy2(src_db, tmp_db)
except Exception as err:
    print("Database copy error:", err)

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
