from rest_framework import serializers

from ...models import Rule

__all__ = ("RuleSerializers",)


class RuleSerializers(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields = ("id", "title", "number", "content")
