from rest_framework import authentication, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import TourRatingCreateSerializer

__all__ = ("TourRatingView",)


class TourRatingView(APIView):
    """
    POST /api/v1/tour/rating/

    Турист оставляет оценку после завершения тура.
    Body: {"device_token": "...", "rating": 4, "comment": "..."}
    """

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = TourRatingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": "ok"}, status=status.HTTP_201_CREATED)
