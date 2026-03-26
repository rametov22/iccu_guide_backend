from rest_framework import serializers
from specialist.models import Specialist, TourSession

__all__ = ("SpecialistSerializer",)


class SpecialistSerializer(serializers.ModelSerializer):
    """Для списка специалистов (экран выбора у туриста)."""

    name = serializers.CharField(source="user.get_full_name", read_only=True)
    avatar = serializers.SerializerMethodField()
    has_active_session = serializers.SerializerMethodField()
    active_session_id = serializers.SerializerMethodField()

    class Meta:
        model = Specialist
        fields = ("id", "name", "number", "avatar", "has_active_session", "active_session_id")

    def get_avatar(self, obj):
        if not obj.avatar:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.avatar.url) if request else obj.avatar.url

    def get_has_active_session(self, obj):
        return obj.sessions.filter(status=TourSession.Status.WAITING).exists()

    def get_active_session_id(self, obj):
        session = obj.sessions.filter(status=TourSession.Status.WAITING).first()
        return session.pk if session else None
