from .base import BASE_DIR

__all__ = (
    "LANGUAGE_CODE",
    "LANGUAGES",
    "TIME_ZONE",
    "USE_I18N",
    "USE_L10N",
    "USE_TZ",
    "MODELTRANSLATION_DEFAULT_LANGUAGE",
    "MODELTRANSLATION_LANGUAGES",
)


LANGUAGE_CODE = "ru"

LANGUAGES = [
    ("ru", "Russian"),
    ("en", "English"),
    ("uz", "Uzbek"),
]

TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [BASE_DIR / "locale"]

MODELTRANSLATION_DEFAULT_LANGUAGE = "ru"
MODELTRANSLATION_LANGUAGES = ("ru", "en", "uz")
