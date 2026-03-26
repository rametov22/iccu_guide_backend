from rest_framework import serializers

from ...models import Hall
from .section import SectionWithExhibitsSerializer

__all__ = ("HallSerializer", "HallTreeSerializer")


class HallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hall
        fields = ("id", "name", "description", "order")


class HallTreeSerializer(serializers.ModelSerializer):
    """Зал с вложенными разделами и экспонатами."""

    sections = SectionWithExhibitsSerializer(many=True, read_only=True)

    class Meta:
        model = Hall
        fields = ("id", "name", "description", "order", "sections")
