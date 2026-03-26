from django.db import models
from rest_framework import generics, permissions

from ...models import Hall, Section, Exhibit
from ..serializers import HallTreeSerializer

__all__ = ("HallTreeView",)


class HallTreeView(generics.ListAPIView):
    """
    GET /api/v1/exhibits/halls/

    Дерево музея: залы → разделы → экспонаты.
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = HallTreeSerializer

    def get_queryset(self):
        return (
            Hall.objects.filter(is_active=True)
            .prefetch_related(
                models.Prefetch(
                    "sections",
                    queryset=Section.objects.filter(is_active=True).order_by("order", "name"),
                ),
                models.Prefetch(
                    "sections__exhibits",
                    queryset=Exhibit.objects.filter(is_active=True).order_by("order", "title"),
                ),
            )
            .order_by("order", "name")
        )
