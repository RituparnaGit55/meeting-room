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

from django.contrib.auth import get_user_model
User = get_user_model()

# Create test user
email = "test@example.com"
password = "test1234"

user, created = User.objects.get_or_create(
    email=email,
    defaults={
        "first_name": "Test",
        "last_name": "User",
        "is_email_verified": True,
    }
)

if created:
    user.set_password(password)
    user.save()
    print("Test user created!")
    print(f"Email: {email}")
    print(f"Password: {password}")
else:
    user.set_password(password)
    user.save()
    print("Test user updated!")
    print(f"Email: {email}")
    print(f"Password: {password}")
