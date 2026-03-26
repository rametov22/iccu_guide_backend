from rest_framework import generics, permissions
from specialist.models import Specialist

from ..serializers import SpecialistSerializer

__all__ = ("SpecialistListView",)


class SpecialistListView(generics.ListAPIView):
    """
    GET /api/specialists/

    Список активных специалистов для туристов.
    Без авторизации.
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = SpecialistSerializer
    queryset = (
        Specialist.objects.filter(
            is_active=True,
            sessions__status="waiting",
        )
        .select_related("user")
        .prefetch_related("sessions")
        .distinct()
    )
