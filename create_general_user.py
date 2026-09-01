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

from apps.accounts.models import User

# Create test user
email = "user@example.com"
password = "user1234"

user, created = User.objects.get_or_create(
    email=email,
    defaults={
        "first_name": "General",
        "last_name": "User",
        "is_email_verified": True,
        "is_staff": False,
        "is_superuser": False,
        "role": "USER",
    }
)

user.set_password(password)
# Ensure it is a general user
user.is_staff = False
user.is_superuser = False
user.role = "USER"
user.save()

print("General user created/updated successfully!")
print(f"Email: {email}")
print(f"Password: {password}")
