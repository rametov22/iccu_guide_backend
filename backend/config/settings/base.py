import os
import sys
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _

from corsheaders.defaults import default_headers, default_methods
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(os.path.join(BASE_DIR, "apps"))

ENVIRONMENT = config("ENVIRONMENT", default="prod")
ALLOWED_ENVIRONMENTS = ("dev", "test", "stage", "prod")
if ENVIRONMENT not in ALLOWED_ENVIRONMENTS:
    raise ImproperlyConfigured(f"ENVIRONMENT must be one of {ALLOWED_ENVIRONMENTS}, got {ENVIRONMENT!r}.")

DEBUG = ENVIRONMENT == "dev"
IS_SECURE_ENV = ENVIRONMENT in ("stage", "prod")

APP_NAME = config("DJANGO_APP_NAME", default="ICCU iPad Tour")
SECRET_KEY = config(
    "DJANGO_SECRET_KEY",
    default=config("SECRET_KEY", default="django-insecure-dev-only-change-me"),
)
if IS_SECURE_ENV and (SECRET_KEY.startswith("django-insecure") or len(SECRET_KEY) < 50):
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be explicitly set to at least 50 characters in stage/prod.")

ALLOWED_HOSTS = config(
    "DJANGO_ALLOWED_HOSTS",
    default="",
    cast=lambda value: [item for part in value.split(",") if (item := part.strip())],
)

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "users.User"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = IS_SECURE_ENV
SECURE_REDIRECT_EXEMPT = [r"^healthcheck/"]
SESSION_COOKIE_SECURE = IS_SECURE_ENV
CSRF_COOKIE_SECURE = IS_SECURE_ENV
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_HSTS_SECONDS = 31536000 if IS_SECURE_ENV else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = IS_SECURE_ENV
SECURE_HSTS_PRELOAD = IS_SECURE_ENV
X_FRAME_OPTIONS = "SAMEORIGIN"

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

CSRF_TRUSTED_ORIGINS = config(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    default="",
    cast=lambda value: [item for part in value.split(",") if (item := part.strip())],
)
CORS_ALLOWED_ORIGINS = config(
    "DJANGO_CORS_ALLOWED_ORIGINS",
    default="",
    cast=lambda value: [item for part in value.split(",") if (item := part.strip())],
)
CORS_ALLOW_HEADERS = (*default_headers,)
CORS_ALLOW_METHODS = (*default_methods,)
CORS_ALLOW_CREDENTIALS = True

INSTALLED_APPS = [
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rosetta",
    "drf_spectacular",
    "drf_yasg",
    "rest_framework",
    "rest_framework_simplejwt",
    "martor",
    "channels",
    "django_structlog",
    "guide.apps.GuideConfig",
    "specialist.apps.SpecialistConfig",
    "users.apps.UsersConfig",
    "exhibit.apps.ExhibitConfig",
    "tour.apps.TourConfig",
    "device.apps.DeviceConfig",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_structlog.middlewares.RequestMiddleware",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB", default="iccu_guide_db"),
        "USER": config("POSTGRES_USER", default="iccu_guide_db_user"),
        "PASSWORD": config("POSTGRES_PASSWORD", default=""),
        "HOST": config("POSTGRES_HOST", default="db"),
        "PORT": config("POSTGRES_PORT", default="5432"),
        "CONN_MAX_AGE": config("POSTGRES_CONN_MAX_AGE", default=60, cast=int),
    }
}

REDIS_HOST = config("REDIS_HOST", default="redis")
REDIS_PORT = config("REDIS_PORT", default=6379, cast=int)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/1",
        "TIMEOUT": 600,
    }
}
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [f"redis://{REDIS_HOST}:{REDIS_PORT}/0"],
        },
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

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

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"
STATICFILES_DIRS = [BASE_DIR / "static_src"]
MEDIA_URL = config("DJANGO_MEDIA_URL", default="/media/")
MEDIA_ROOT = BASE_DIR / "media"

LANGUAGE_CODE = "ru"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True
LANGUAGES = (
    ("ru", _("Русский")),
    ("en", _("English")),
    ("uz", _("O‘zbekcha")),
)
LOCALE_PATHS = [BASE_DIR / "locale"]
MODELTRANSLATION_DEFAULT_LANGUAGE = "ru"
MODELTRANSLATION_LANGUAGES = ("ru", "en", "uz")
