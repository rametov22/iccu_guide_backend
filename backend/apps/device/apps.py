from django.apps import AppConfig


class DeviceConfig(AppConfig):
    name = "device"

    def ready(self):
        from . import signals  # noqa: F401
