from rest_framework import serializers

from ...models import Device, DeviceFileState

__all__ = (
    "DeviceRegisterSerializer",
    "DeviceSerializer",
    "DeviceFileStateSerializer",
    "DeviceFileStateUpdateSerializer",
    "DeviceAdminSerializer",
)


class DeviceRegisterSerializer(serializers.Serializer):
    """Вход POST /devices/register/."""

    fcm_token = serializers.CharField(max_length=512)
    name = serializers.CharField(max_length=64, required=False, allow_blank=True, default="")


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ("id", "fcm_token", "name", "is_active",
                  "last_seen_at", "created_at")
        read_only_fields = fields


class DeviceFileStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceFileState
        fields = ("file_url", "status", "progress", "file_size",
                  "error_message", "updated_at")
        read_only_fields = ("updated_at",)


class DeviceFileStateUpdateSerializer(serializers.Serializer):
    """Вход POST /devices/<id>/file-status/."""

    file_url = serializers.CharField(max_length=500)
    status = serializers.ChoiceField(choices=DeviceFileState.Status.choices)
    progress = serializers.IntegerField(min_value=0, max_value=100, required=False, default=0)
    file_size = serializers.IntegerField(min_value=0, required=False, default=0)
    error_message = serializers.CharField(required=False, allow_blank=True, default="", max_length=500)


class DeviceAdminSerializer(serializers.ModelSerializer):
    """Для админ-дашборда — устройство + сводка по скачиванию."""

    files_total = serializers.IntegerField(read_only=True)
    files_done = serializers.IntegerField(read_only=True)
    files_error = serializers.IntegerField(read_only=True)
    files_pending = serializers.IntegerField(read_only=True)

    class Meta:
        model = Device
        fields = ("id", "fcm_token", "name", "is_active",
                  "last_seen_at", "created_at",
                  "files_total", "files_done", "files_error", "files_pending")
        read_only_fields = fields
