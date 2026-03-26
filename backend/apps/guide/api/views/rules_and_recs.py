from rest_framework import generics

from ...models import Rule
from ..serializers import RuleSerializers

__all__ = ("RuleApiView",)


class RuleApiView(generics.ListAPIView):
    serializer_class = RuleSerializers
    queryset = Rule.objects.filter(is_active=True)
