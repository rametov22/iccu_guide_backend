from guide.api.serializers import SpecialistSerializer
from rest_framework import serializers

from ...models import TourSession

__all__ = ("TourSessionSerializer",)


class TourSessionSerializer(serializers.ModelSerializer):
    specialist = SpecialistSerializer(read_only=True)
    current_section_name = serializers.CharField(
        source="current_section.name", read_only=True, default=None
    )

    class Meta:
        model = TourSession
        fields = (
            "id",
            "specialist",
            "status",
            "tourist_count",
            "current_section",
            "current_section_name",
            "created_at",
        )
