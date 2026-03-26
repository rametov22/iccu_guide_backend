from decouple import config

__all__ = ("INSTALLED_APPS",)


DJANGO_APPS = [
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rosetta",
    "drf_yasg",
    "martor",
    "drf_spectacular",
    "channels",
]


LOCAL_APPS = [
    "guide",
    "specialist",
    "users",
    "exhibit",
    "tour",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
