from rest_framework import serializers

from specialist.models import TourSession
from tour.models import TouristSession

__all__ = (
    "TouristJoinSerializer",
    "TouristSessionSerializer",
    "TouristRegisterSerializer",
    "TouristDeviceSerializer",
)


class TouristJoinSerializer(serializers.Serializer):
    """Турист подключается к специалисту по номеру."""

    specialist_number = serializers.IntegerField(
        help_text="Номер специалиста на бейдже",
    )
    device_token = serializers.IntegerField(
        help_text="Номер устройства туриста (1-600)",
    )


class TouristSessionSerializer(serializers.ModelSerializer):
    specialist_name = serializers.CharField(
        source="specialist.name", read_only=True
    )
    specialist_number = serializers.IntegerField(
        source="specialist.number", read_only=True
    )

    class Meta:
        model = TourSession
        fields = (
            "id",
            "specialist_name",
            "specialist_number",
            "status",
            "tourist_count",
        )


class TouristRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = TouristSession
        fields = ("id", "device_token")
        read_only_fields = ("id", "device_token")


class TouristDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TouristSession
        fields = ("id", "device_token", "is_active", "joined_at", "created_at")
        read_only_fields = fields
