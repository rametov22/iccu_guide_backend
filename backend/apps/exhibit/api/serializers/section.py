from rest_framework import serializers

from ...models import Section
from .exhibit import ExhibitSerializer

__all__ = ("SectionSerializer", "SectionWithExhibitsSerializer")


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ("id", "name", "description", "order", "duration_seconds", "break_duration_seconds", "hall")


class SectionWithExhibitsSerializer(serializers.ModelSerializer):
    """Раздел с вложенными экспонатами."""

    exhibits = ExhibitSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ("id", "name", "description", "order", "duration_seconds", "break_duration_seconds", "exhibits")
