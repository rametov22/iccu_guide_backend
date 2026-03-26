from .redis import REDIS_HOST, REDIS_PORT

__all__ = ("CHANNEL_LAYERS",)


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
        },
    },
}
