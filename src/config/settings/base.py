import os
from pathlib import Path
from datetime import timedelta
import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
IS_VERCEL = os.getenv("VERCEL") == "1" or os.getenv("VERCEL_ENV") is not None

load_dotenv(os.path.join(BASE_DIR.parent, ".env"))

SECRET_KEY = os.getenv("SECRET_KEY") or "django-insecure-placeholder-key-change-me"

DEBUG = True

raw_allowed_hosts = os.getenv("ALLOWED_HOSTS", "")
env_hosts = [h.strip() for h in raw_allowed_hosts.split(",") if h.strip()]

ALLOWED_HOSTS = [
    "*",
    ".vercel.app",
    "*.vercel.app",
    "localhost",
    "127.0.0.1",
] + env_hosts

# Security & Proxy Settings for Vercel / Reverse Proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8001",
    "http://127.0.0.1:8001",
    "https://*.vercel.app",
]
raw_csrf_origins = os.getenv("CSRF_TRUSTED_ORIGINS", "")
if raw_csrf_origins:
    CSRF_TRUSTED_ORIGINS += [o.strip() for o in raw_csrf_origins.split(",") if o.strip()]
if os.getenv("VERCEL_URL"):
    CSRF_TRUSTED_ORIGINS.append(f"https://{os.getenv('VERCEL_URL')}")

CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"

AUTH_USER_MODEL = "accounts.User"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "channels",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "apps.accounts",
    "apps.meetings",
    # "apps.participants",
    "apps.chat",
    "apps.recordings",
    "apps.transcripts",
    "apps.summaries",
    "apps.tasks",
    "apps.notifications",
    "apps.analytics",
    # "apps.webhooks",
    # "apps.api_keys",
    "apps.dashboard",
]

if not IS_VERCEL:
    INSTALLED_APPS.insert(0, "daphne")

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Support Vercel serverless environment (writable /tmp filesystem for SQLite)
IS_VERCEL = os.getenv("VERCEL") == "1" or os.getenv("VERCEL_ENV") is not None
if IS_VERCEL and not os.getenv("DATABASE_URL"):
    temp_dir = Path("/tmp") if os.name != "nt" else Path(os.environ.get("TEMP", os.environ.get("TMP", BASE_DIR / "scratch")))
    temp_dir.mkdir(parents=True, exist_ok=True)
    db_file_path = str(temp_dir / "db.sqlite3")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": db_file_path,
        }
    }
else:
    DATABASES = {
        "default": dj_database_url.config(
            default=f"sqlite:///{os.path.join(BASE_DIR, 'db.sqlite3')}",
            conn_max_age=600,
            conn_health_checks=True,
        )
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": os.getenv("JWT_SECRET_KEY") or SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# Email Configuration
if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
email_port_raw = (os.getenv("EMAIL_PORT") or "").strip()
EMAIL_PORT = int(email_port_raw) if email_port_raw.isdigit() else 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "webmaster@localhost")

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID") or ""
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET") or ""
default_site_domain = f"https://{os.getenv('VERCEL_URL')}" if os.getenv("VERCEL_URL") else "http://localhost:8000"
SITE_DOMAIN = os.getenv("SITE_DOMAIN") or default_site_domain
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI") or f"{SITE_DOMAIN}/accounts/google/login/callback/"

# AssemblyAI Configuration
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# YouTube Upload Configuration
YOUTUBE_API_CREDENTIALS_FILE = os.getenv("YOUTUBE_API_CREDENTIALS_FILE")
YOUTUBE_DEFAULT_VISIBILITY = os.getenv("YOUTUBE_DEFAULT_VISIBILITY", "private")

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# Uncomment for Redis in production
# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels_redis.core.RedisChannelLayer",
#         "CONFIG": {
#             "hosts": [os.getenv("REDIS_URL", "redis://localhost:6379/1")],
#         },
#     },
# }

# Celery configuration (requires Redis)
# CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/2")
# CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
# CELERY_ACCEPT_CONTENT = ["json"]
# CELERY_TASK_SERIALIZER = "json"
# CELERY_RESULT_SERIALIZER = "json"
# CELERY_TIMEZONE = "UTC"

LOGIN_URL = "/auth/login/"
LOGIN_REDIRECT_URL = "/"

# Authentication Backends & django-allauth Configuration
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_LOGIN_ON_GET = True
ACCOUNT_ADAPTER = "apps.accounts.adapter.CustomAccountAdapter"
SOCIALACCOUNT_ADAPTER = "apps.accounts.adapter.CustomSocialAccountAdapter"


SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
        "APP": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
            "secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
            "key": ""
        }
    }
}


