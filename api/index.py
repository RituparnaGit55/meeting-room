import os
import sys
import shutil
import traceback
from pathlib import Path

# Add src folder to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

# Copy seed database to writable temp folder on serverless startup if missing
temp_dir = Path("/tmp") if os.name != "nt" else Path(os.environ.get("TEMP", os.environ.get("TMP", BASE_DIR / "scratch")))

try:
    temp_dir.mkdir(parents=True, exist_ok=True)
    tmp_db = temp_dir / "db.sqlite3"
    src_db = SRC_DIR / "db.sqlite3"

    if src_db.exists() and not tmp_db.exists():
        shutil.copy2(src_db, tmp_db)
except Exception as err:
    print("Database copy error:", err)

_application = None

def get_app():
    global _application
    if _application is None:
        from django.core.wsgi import get_wsgi_application
        _application = get_wsgi_application()
    return _application

def app(environ, start_response):
    try:
        handler = get_app()
        return handler(environ, start_response)
    except Exception as e:
        error_details = traceback.format_exc()
        print("Vercel Function Error:\n", error_details, file=sys.stderr)
        status = "500 Internal Server Error"
        response_headers = [("Content-Type", "text/html; charset=utf-8")]
        start_response(status, response_headers)
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>MeetFlow Deployment Diagnostic</title></head>
        <body style="font-family: sans-serif; padding: 2rem; background: #0f172a; color: #f8fafc;">
            <h2 style="color: #ef4444;">MeetFlow Serverless Exception Traceback</h2>
            <pre style="background: #1e293b; color: #f1f5f9; padding: 1.5rem; border-radius: 8px; overflow-x: auto; white-space: pre-wrap;">{error_details}</pre>
        </body>
        </html>
        """
        return [html.encode("utf-8")]

handler = app
application = app
