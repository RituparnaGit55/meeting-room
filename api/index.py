import os
import sys
import shutil
import traceback
from pathlib import Path

# Add src directory to Python path
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
    print("Database copy error:", err, file=sys.stderr)

from django.core.wsgi import get_wsgi_application

try:
    _django_app = get_wsgi_application()
except Exception as e:
    print("Django initialization error:", traceback.format_exc(), file=sys.stderr)
    _django_app = None

def handler(environ, start_response):
    global _django_app
    if _django_app is None:
        try:
            _django_app = get_wsgi_application()
        except Exception as e:
            err_msg = traceback.format_exc()
            print("Django lazy init error:", err_msg, file=sys.stderr)
            status = "500 Internal Server Error"
            headers = [("Content-Type", "text/plain; charset=utf-8")]
            start_response(status, headers)
            return [f"Django Initialization Error:\n\n{err_msg}".encode("utf-8")]
    
    try:
        return _django_app(environ, start_response)
    except Exception as e:
        err_msg = traceback.format_exc()
        print("Request execution error:", err_msg, file=sys.stderr)
        status = "500 Internal Server Error"
        headers = [("Content-Type", "text/plain; charset=utf-8")]
        start_response(status, headers)
        return [f"Request Execution Error:\n\n{err_msg}".encode("utf-8")]

app = handler
