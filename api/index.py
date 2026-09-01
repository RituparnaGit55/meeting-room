import os
import sys
from pathlib import Path

# Add src folder to Python path for Django import resolution
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

from config.wsgi import application

# Vercel serverless function entrypoint
app = application
