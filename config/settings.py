# config/settings.py

from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-CHANGE-THIS-IN-PRODUCTION"
DEBUG      = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    # GreenTrace
    "greentrace",
]

AUTH_USER_MODEL = "greentrace.User"

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",          # MUST be first
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME"  : BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE     = "Europe/Tirane"
USE_I18N      = True
USE_TZ        = True

STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL   = "/media/"
MEDIA_ROOT  = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Django REST Framework ─────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

# ── JWT ───────────────────────────────────────────────────────────
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME"    : timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME"   : timedelta(days=7),
    "ROTATE_REFRESH_TOKENS"    : True,
    "BLACKLIST_AFTER_ROTATION" : True,
}

# ── CORS (allow React dev server on port 3000) ────────────────────
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# ── Celery (Phase 2) ──────────────────────────────────────────────
CELERY_BROKER_URL        = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND    = "redis://localhost:6379/0"
CELERY_TIMEZONE          = "Europe/Tirane"
CELERY_TASK_TRACK_STARTED = True

# Celery Beat schedule (UC-21 daily + UC-17 weekly)
from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {
    "check-overdue-milestones-daily": {
        "task"    : "greentrace.check_overdue_milestones",
        "schedule": crontab(hour=7, minute=0),   # every day at 07:00
    },
    "send-weekly-digest": {
        "task"    : "greentrace.send_weekly_digest",
        "schedule": crontab(hour=8, minute=0, day_of_week=1),  # Monday 08:00
    },
}

# ── Email (replace with real SMTP in production) ──────────────────
EMAIL_BACKEND       = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL  = "noreply@greentrace.al"
# Fix "View Site" button in Django admin
DJANGO_ADMIN_SITE_URL = "http://localhost:3000"