import os
import sys
from pathlib import Path

from corsheaders.defaults import default_headers, default_methods
from decouple import config

__all__ = (
    "BASE_DIR",
    "APP_NAME",
    "SECRET_KEY",
    "DEBUG",
    "SECURE_SSL_REDIRECT",
    "SESSION_COOKIE_SECURE",
    "SECURE_PROXY_SSL_HEADER",
    "ALLOWED_HOSTS",
    "CSRF_TRUSTED_ORIGINS",
    "CORS_ALLOWED_ORIGINS",
    "CORS_ALLOW_HEADERS",
    "CORS_ALLOW_METHODS",
    "CORS_ALLOW_CREDENTIALS",
    "WSGI_APPLICATION",
    "ASGI_APPLICATION",
    "ROOT_URLCONF",
    "DEFAULT_AUTO_FIELD",
)


BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(os.path.join(BASE_DIR, "apps"))

APP_NAME = config("DJANGO_APP_NAME", default="AppName")

SECRET_KEY = config("SECRET_KEY")

X_FRAME_OPTIONS = "SAMEORIGIN"

DEBUG = config("DEBUG", cast=bool, default=True)

INTERNAL_IPS = ("127.0.0.1",)


SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


ALLOWED_HOSTS = config(
    "DJANGO_ALLOWED_HOSTS",
    default="",
    cast=lambda v: [x for s in v.split(",") if (x := s.strip())],
)


CSRF_TRUSTED_ORIGINS = config(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    default="",
    cast=lambda v: [x for s in v.split(",") if (x := s.strip())],
)

CORS_ALLOWED_ORIGINS = config(
    "DJANGO_CORS_ALLOWED_ORIGINS",
    default="",
    cast=lambda v: [x for s in v.split(",") if (x := s.strip())],
)

CORS_ALLOW_HEADERS = (
    *default_headers,
    # "my-custom-header",
)

CORS_ALLOW_METHODS = (
    *default_methods,
    # "POKE",
)

CORS_ALLOW_CREDENTIALS = True


WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


ROOT_URLCONF = "config.urls"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
