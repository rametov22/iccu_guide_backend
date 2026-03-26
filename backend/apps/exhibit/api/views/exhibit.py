from rest_framework import generics, permissions

from ...models import Exhibit
from ..serializers import ExhibitSerializer

__all__ = ("ExhibitsBySectionView",)


class ExhibitsBySectionView(generics.ListAPIView):
    """
    GET /api/v1/exhibits/sections/{section_id}/exhibits/

    Экспонаты по конкретному разделу.
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = ExhibitSerializer

    def get_queryset(self):
        section_id = self.kwargs["section_id"]
        return Exhibit.objects.filter(
            section_id=section_id,
            is_active=True,
        )
