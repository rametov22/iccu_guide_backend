from datetime import timedelta

from decouple import config

__all__ = ("REST_FRAMEWORK", "SIMPLE_JWT")


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(seconds=config("JWT_ACCESS_LIFETIME_SECONDS", default=300, cast=int)),
    "REFRESH_TOKEN_LIFETIME": timedelta(hours=config("JWT_REFRESH_LIFETIME_HOURS", default=5, cast=int)),
}


REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # "DEFAULT_AUTHENTICATION_CLASSES": (
    #     "rest_framework_simplejwt.authentication.JWTAuthentication",
    # ),
    # "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S%z",
    # "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    # "PAGE_SIZE": 10,
    # "DEFAULT_RENDERER_CLASSES": [
    #     "rest_framework.renderers.JSONRenderer",
    #     "rest_framework.renderers.BrowsableAPIRenderer",
    # ],
}
