from decouple import config

__all__ = (
    "REDIS_HOST",
    "REDIS_PORT",
    "CACHES",
)


REDIS_HOST = config("REDIS_HOST", default="redis")
REDIS_PORT = config("REDIS_PORT", default=6379, cast=int)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}",
        "TIMEOUT": 600,
    }
}
