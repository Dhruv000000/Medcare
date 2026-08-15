"""
Django settings for the MediCare backend foundation.

Phase 4 prepares this project for the user's Windows PostgreSQL 18.6 instance.
Authentication and business APIs are implemented; Phase 18 adds only the fixed academic inference API. Broader AI capabilities remain deferred.
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_local_env(path: Path) -> None:
    """Load simple KEY=VALUE entries without overriding process environment values."""

    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if key and key not in os.environ:
            os.environ[key] = value


# Local development convenience only. backend/.env is ignored by Git and must
# never contain credentials that are committed or copied into documentation.
_load_local_env(BASE_DIR / ".env")

DEPLOYMENT_ENV = os.environ.get("DJANGO_ENV", "development").strip().lower()
IS_PRODUCTION = DEPLOYMENT_ENV in {"production", "prod"}

# Development-safe placeholder only. Production requires an explicit secret.
_secret_key = os.environ.get("DJANGO_SECRET_KEY", "").strip()
if IS_PRODUCTION and not _secret_key:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set when DJANGO_ENV=production.")
SECRET_KEY = _secret_key or "dev-only-placeholder-change-before-deployment"

DEBUG = os.environ.get("DEBUG", "True").strip().lower() in {"1", "true", "yes", "on"}
if IS_PRODUCTION and DEBUG:
    raise ImproperlyConfigured("DEBUG must be false when DJANGO_ENV=production.")

_allowed_hosts_value = os.environ.get("ALLOWED_HOSTS", "").strip()
if IS_PRODUCTION and not _allowed_hosts_value:
    raise ImproperlyConfigured("ALLOWED_HOSTS must be set when DJANGO_ENV=production.")
ALLOWED_HOSTS = [
    host.strip()
    for host in (_allowed_hosts_value or "127.0.0.1,localhost").split(",")
    if host.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "apps.accounts",
    "apps.appointments",
    "apps.health",
    "apps.medical_records",
    "apps.prescriptions",
    "apps.reports",
    "apps.clinical_api",
    "apps.admin_api",
    "apps.ai_api",
    "apps.ai_audit",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "config.middleware.LocalFrontendCorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# When all DB_* values are present, Django targets the user's Windows PostgreSQL
# instance. Without them, SQLite is retained only for sandbox-safe configuration
# and URL/health checks; this fallback does not verify PostgreSQL connectivity.
DB_NAME = os.environ.get("DB_NAME", "").strip()
DB_USER = os.environ.get("DB_USER", "").strip()
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_HOST = os.environ.get("DB_HOST", "localhost").strip()
DB_PORT = os.environ.get("DB_PORT", "5432").strip()

POSTGRES_CONFIGURED = all(
    [DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT]
)

if POSTGRES_CONFIGURED:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": DB_NAME,
            "USER": DB_USER,
            "PASSWORD": DB_PASSWORD,
            "HOST": DB_HOST,
            "PORT": DB_PORT,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
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
# Phase 24: protected clinical attachments are served only by authorized API views.
MEDIA_ROOT = BASE_DIR / "protected_media"
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024

# The static multi-page frontend (HTML/CSS/JS) lives outside the Django app in
# ../frontend and is served at the site root by WhiteNoise alongside Django's
# own /static/ assets (admin, DRF browsable API).
FRONTEND_DIR = BASE_DIR.parent / "frontend"
if FRONTEND_DIR.exists():
    WHITENOISE_ROOT = FRONTEND_DIR

if IS_PRODUCTION:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"

_frontend_origins_value = os.environ.get("FRONTEND_ALLOWED_ORIGINS", "").strip()
if IS_PRODUCTION and not _frontend_origins_value:
    raise ImproperlyConfigured(
        "FRONTEND_ALLOWED_ORIGINS must be set when DJANGO_ENV=production."
    )
FRONTEND_ALLOWED_ORIGINS = {
    origin.strip()
    for origin in (
        _frontend_origins_value or "http://127.0.0.1:8010,http://localhost:8010"
    ).split(",")
    if origin.strip()
}
CSRF_TRUSTED_ORIGINS = sorted(FRONTEND_ALLOWED_ORIGINS)
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = IS_PRODUCTION
CSRF_COOKIE_SECURE = IS_PRODUCTION
SECURE_SSL_REDIRECT = IS_PRODUCTION
SECURE_HSTS_SECONDS = 31536000 if IS_PRODUCTION else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = IS_PRODUCTION
SECURE_HSTS_PRELOAD = IS_PRODUCTION
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
ADMIN_REGISTRATION_CODE = os.environ.get("ADMIN_REGISTRATION_CODE", "").strip()

# Symptom chatbot (patient-facing) via the Groq chat completions API.
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile").strip()

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "ai_inference": "60/min",
    },
}
