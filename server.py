
import os
import sys
import traceback
from pathlib import Path

# Set up paths
project_dir = Path(__file__).parent
src_dir = project_dir / "src"
os.chdir(src_dir)
sys.path.insert(0, str(src_dir))

# Set Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

try:
    print("Importing Django...")
    import django
    django.setup()
    
    print("Starting Django development server on http://127.0.0.1:8001/")
    from django.core.management import execute_from_command_line
    
    # Run the server with noreload on port 8001
    execute_from_command_line(["manage.py", "runserver", "127.0.0.1:8001", "--noreload"])
    
except Exception as e:
    print(f"ERROR: {str(e)}")
    print("Traceback:")
    print(traceback.format_exc())
    input("Press Enter to exit...")
