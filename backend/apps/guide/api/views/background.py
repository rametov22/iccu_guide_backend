from rest_framework import generics, permissions

from guide.models import Background
from ..serializers.background import BackgroundSerializer

__all__ = ("BackgroundListView",)


class BackgroundListView(generics.ListAPIView):
    """GET /api/v1/guide/backgrounds/ — список фоновых изображений."""

    permission_classes = [permissions.AllowAny]
    serializer_class = BackgroundSerializer
    queryset = Background.objects.filter(is_active=True)
