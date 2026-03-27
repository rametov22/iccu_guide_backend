from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models as db_models
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from tour.models import TouristSession
from ...models import TourSession
from ..serializers import TourSessionSerializer


def _notify_lobby_specialists():
    """Notify lobby WS about specialist list change."""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "lobby",
        {"type": "specialist.update"},
    )

__all__ = (
    "TourSessionDetailView",
    "TourSessionCreateView",
    "TourSessionTouristListView",
    "TourSessionTouristAddView",
    "TourSessionTouristKickView",
)


class TourSessionDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/specialist/sessions/{id}/

    Информация о сессии тура.
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = TourSessionSerializer
    queryset = TourSession.objects.select_related("specialist__user")


class TourSessionCreateView(APIView):
    """
    POST /api/v1/specialist/sessions/create/

    Специалист создаёт новую сессию в статусе WAITING.
    Проверяет, что нет активной (незавершённой) сессии.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            specialist = request.user.specialist_profile
        except Exception:
            return Response(
                {"error": "Пользователь не является специалистом"},
                status=status.HTTP_403_FORBIDDEN,
            )

        active_session = TourSession.objects.filter(
            specialist=specialist,
        ).exclude(
            status=TourSession.Status.FINISHED,
        ).first()

        if active_session:
            return Response(
                {
                    "error": "У вас уже есть активная сессия",
                    "session_id": active_session.pk,
                },
                status=status.HTTP_409_CONFLICT,
            )

        session = TourSession.objects.create(specialist=specialist)
        _notify_lobby_specialists()
        return Response(
            TourSessionSerializer(session).data,
            status=status.HTTP_201_CREATED,
        )


class TourSessionTouristListView(APIView):
    """
    GET /api/v1/specialist/sessions/{id}/tourists/

    Список туристов в сессии.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        tourists = TouristSession.objects.filter(
            tour_session_id=pk, is_active=True
        ).order_by("tour_number").values(
            "id", "device_token", "tour_number", "device_name", "ip_address", "joined_at", "created_at"
        )

        return Response(list(tourists))


class TourSessionTouristAddView(APIView):
    """
    POST /api/v1/specialist/sessions/{id}/tourists/add/

    Специалист вручную добавляет туриста в сессию по device_token.
    Body: {"device_token": "..."}
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        device_token = request.data.get("device_token", "").strip()
        if not device_token:
            return Response({"error": "device_token обязателен"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = TourSession.objects.get(pk=pk)
        except TourSession.DoesNotExist:
            return Response({"error": "Сессия не найдена"}, status=status.HTTP_404_NOT_FOUND)

        try:
            tourist = TouristSession.objects.get(device_token=device_token, is_active=True)
        except TouristSession.DoesNotExist:
            return Response({"error": "Турист с таким токеном не найден"}, status=status.HTTP_404_NOT_FOUND)

        # Присваиваем порядковый номер в туре
        max_num = (
            TouristSession.objects.filter(tour_session=session)
            .aggregate(db_models.Max("tour_number"))["tour_number__max"]
            or 0
        )
        tourist.tour_session = session
        tourist.joined_at = timezone.now()
        tourist.tour_number = max_num + 1
        tourist.save(update_fields=["tour_session", "joined_at", "tour_number"])

        real_count = TouristSession.objects.filter(tour_session=session, is_active=True).count()
        session.tourist_count = real_count
        session.save(update_fields=["tourist_count"])

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"tour_{pk}",
            {
                "type": "tourist.joined",
                "tourist_count": real_count,
                "tourist_id": tourist.pk,
                "device_token": str(tourist.device_token),
            },
        )

        # Уведомляем lobby-WS туриста
        async_to_sync(channel_layer.group_send)(
            f"lobby_{tourist.device_token}",
            {
                "type": "session.assigned",
                "session_id": session.pk,
                "specialist_name": session.specialist.name,
                "specialist_number": session.specialist.number,
            },
        )

        return Response({"status": "ok", "tourist_id": tourist.pk}, status=status.HTTP_200_OK)


class TourSessionTouristKickView(APIView):
    """
    DELETE /api/v1/specialist/sessions/{id}/tourists/{tourist_id}/

    Кикнуть туриста из сессии.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk, tourist_id):
        try:
            tourist = TouristSession.objects.get(
                pk=tourist_id, tour_session_id=pk, is_active=True
            )
        except TouristSession.DoesNotExist:
            return Response(
                {"error": "Турист не найден"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Отвязываем от сессии — турист возвращается в лобби
        device_token = tourist.device_token
        tourist.tour_session = None
        tourist.tour_number = None
        tourist.joined_at = None
        tourist.save(update_fields=["tour_session", "tour_number", "joined_at"])

        # Обновляем tourist_count
        session = TourSession.objects.get(pk=pk)
        session.tourist_count = TouristSession.objects.filter(
            tour_session=session, is_active=True
        ).count()
        session.save(update_fields=["tourist_count"])

        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()

        # Уведомляем туриста лично — его WS закроется
        async_to_sync(channel_layer.group_send)(
            f"tourist_{device_token}",
            {
                "type": "tourist.kicked",
                "tourist_id": tourist_id,
                "device_token": str(device_token),
            },
        )

        # Уведомляем группу тура (специалиста) об обновлённом списке
        async_to_sync(channel_layer.group_send)(
            f"tour_{pk}",
            {
                "type": "tourist.kicked.broadcast",
                "tourist_id": tourist_id,
                "device_token": str(device_token),
                "tourist_count": session.tourist_count,
            },
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
