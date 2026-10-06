"""
Django settings for carnaval project.

Every value comes from the environment: a required secret fails loudly when
absent rather than defaulting (SEC-46 / NFR-09). A gitignored `.env` at the
repository root supplies development values — see `.env.example`.
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

# backend/
BASE_DIR = Path(__file__).resolve().parent.parent
# Monorepo root, where the local `.env` lives.
REPO_DIR = BASE_DIR.parent

load_dotenv(REPO_DIR / ".env")

# SEC-46 / NFR-09: no default secret, ever. Absence is an error, not a value.
if "SECRET_KEY" not in os.environ:
    raise ImproperlyConfigured(
        "SECRET_KEY is not set. Export it as an environment variable, or copy "
        ".env.example to .env at the repository root and fill it in. "
        "Settings never fall back to a default secret (SEC-46 / NFR-09)."
    )
SECRET_KEY = os.environ["SECRET_KEY"]

# DEBUG defaults to False: an unset variable must behave like production.
DEBUG = os.environ.get("DEBUG", "").lower() in ("1", "true", "yes")

_allowed_hosts = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1")
if _allowed_hosts:
    ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts.split(",") if h.strip()]
else:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # ADR 0005: TOTP second factor plus single-use recovery codes.
    "django_otp",
    "django_otp.plugins.otp_static",
    "django_otp.plugins.otp_totp",
    "rest_framework",
    "drf_spectacular",
    "carnaval.core",
    "carnaval.programme",
    "carnaval.ingestion",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # ADR 0005: must follow AuthenticationMiddleware (django-otp docs).
    "django_otp.middleware.OTPMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "carnaval.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "carnaval.wsgi.application"


# Database
# ADR 0009: PostgreSQL 16 is the database. DB_* environment variables enable
# it (production, CI); without them a development machine falls back to SQLite
# so the skeleton runs at zero infrastructure cost. SQLite is never the
# deployment target — ADR 0009 rejected it for deployment explicitly.
if os.environ.get("DB_NAME"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["DB_NAME"],
            "USER": os.environ.get("DB_USER", ""),
            "PASSWORD": os.environ.get("DB_PASSWORD", ""),
            "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
            "PORT": os.environ.get("DB_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(BASE_DIR / "db.sqlite3"),
        }
    }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        )
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ADR 0005: Argon2id is the password hasher (argon2-cffi backs Django's
# Argon2PasswordHasher). PBKDF2 remains only as a fallback for any hash
# created before the switch.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
]

# ADR 0005: the session cookie is httpOnly (Django default, stated because it
# is a decision), Secure, SameSite=Lax. Secure is tied to DEBUG because the
# development server speaks plain HTTP.
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = not DEBUG

# Production transport security, gated on DEBUG so local HTTP development still
# works. `python manage.py check --deploy` is clean with DEBUG off; CI runs it.
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 0 if DEBUG else 31_536_000  # one year
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
# Trust X-Forwarded-Proto only when a reverse proxy that strips it terminates
# TLS. Default off: a directly exposed app must not let a client spoof "https"
# and bypass SECURE_SSL_REDIRECT.
if os.environ.get("TRUST_PROXY_SSL_HEADER", "").lower() in ("1", "true", "yes"):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# REST Framework
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # Fail closed: an endpoint is authenticated-only until it declares
    # otherwise. RBAC is enforced server-side on every request (ADR 0005);
    # the interface hiding a control is never the control. Public read
    # endpoints opt in explicitly with an AllowAny-style permission.
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    # ADR 0005: server-side sessions only. No tokens of any kind, no Basic.
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication"
    ],
}

# Spectacular
SPECTACULAR_SETTINGS = {
    "TITLE": "Carnaval de Pasto API",
    "DESCRIPTION": "API for Carnaval de Pasto project",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# Ingestion pipeline (FR-B). Read at call time by the ingestion package so a
# test can override any of them.
INGESTION_CONTACT_EMAIL = os.environ.get(
    "INGESTION_CONTACT_EMAIL", "victorloal513@gmail.com"
)
INGESTION_HTTP_TIMEOUT = float(os.environ.get("INGESTION_HTTP_TIMEOUT", "30"))
INGESTION_RETRY_BASE = int(os.environ.get("INGESTION_RETRY_BASE", "5"))
INGESTION_RETRY_ATTEMPTS = int(os.environ.get("INGESTION_RETRY_ATTEMPTS", "3"))
INGESTION_RETRY_CAP = int(os.environ.get("INGESTION_RETRY_CAP", "300"))
INGESTION_BREAKER_THRESHOLD = int(os.environ.get("INGESTION_BREAKER_THRESHOLD", "5"))
INGESTION_ROBOTS_CACHE_SECONDS = int(
    os.environ.get("INGESTION_ROBOTS_CACHE_SECONDS", "86400")
)
# Raw payloads live outside git (`data/` is ignored). ADR 0015 picks the
# provider; this path is the swap point for object storage.
INGESTION_RAW_ROOT = Path(
    os.environ.get("INGESTION_RAW_ROOT", str(REPO_DIR / "data" / "raw"))
)
INGESTION_RAW_RETENTION_DAYS = int(os.environ.get("INGESTION_RAW_RETENTION_DAYS", "30"))
INGESTION_RAW_RETENTION_BYTES = int(
    os.environ.get("INGESTION_RAW_RETENTION_BYTES", str(50_000_000))
)
# The edition the pipeline is populating. When set, records outside that year
# fail the sanity gate: the source currently serves a mostly six-year-old
# programme, and "42 records" is not evidence the fetch was correct.
INGESTION_TARGET_YEAR = os.environ.get("INGESTION_TARGET_YEAR", "")

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
