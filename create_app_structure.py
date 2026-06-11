import os

apps = [
    "accounts",
    "meetings",
    "participants",
    "chat",
    "recordings",
    "transcripts",
    "summaries",
    "tasks",
    "notifications",
    "analytics",
    "webhooks",
    "api_keys",
    "dashboard",
]

base_dir = r"c:\Users\ritup\OneDrive\Desktop\meeting_sw\src\apps"

for app in apps:
    app_dir = os.path.join(base_dir, app)
    
    # Create directories
    os.makedirs(os.path.join(app_dir, "services"), exist_ok=True)
    os.makedirs(os.path.join(app_dir, "repositories"), exist_ok=True)
    os.makedirs(os.path.join(app_dir, "consumers"), exist_ok=True)
    os.makedirs(os.path.join(app_dir, "tasks"), exist_ok=True)
    os.makedirs(os.path.join(app_dir, "utils"), exist_ok=True)
    os.makedirs(os.path.join(app_dir, "exceptions"), exist_ok=True)
    os.makedirs(os.path.join(app_dir, "tests"), exist_ok=True)
    
    # Create __init__.py files
    for dir_name in ["services", "repositories", "consumers", "tasks", "utils", "exceptions", "tests"]:
        with open(os.path.join(app_dir, dir_name, "__init__.py"), "w") as f:
            pass

print("All app directories created!")
