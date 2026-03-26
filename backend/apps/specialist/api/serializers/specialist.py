from rest_framework import serializers

from ...models import Specialist

__all__ = ("SpecialistProfileSerializer",)


class SpecialistProfileSerializer(serializers.ModelSerializer):
    """Профиль для самого специалиста (после логина)."""

    name = serializers.CharField(source="user.get_full_name", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Specialist
        fields = ("id", "name", "username", "number", "avatar", "is_active")

    def get_avatar(self, obj):
        if not obj.avatar:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.avatar.url) if request else obj.avatar.url
