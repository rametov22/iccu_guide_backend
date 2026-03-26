from rest_framework import generics, permissions

from guide.models import Guide
from ..serializers import GuideSerializer

__all__ = ("GuideListView",)


class GuideListView(generics.ListAPIView):
    """
    GET /api/v1/guide/guides/

    Список активных виртуальных гидов для туристов.
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = GuideSerializer
    queryset = Guide.objects.filter(is_active=True).order_by("order", "name")
