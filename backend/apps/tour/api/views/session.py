from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models as db_models
from django.utils import timezone
from rest_framework import authentication, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from specialist.models import Specialist, TourSession
from tour.models import TouristSession
from tour.models.tourist_session import _next_device_token
from ..serializers import (
    TouristJoinSerializer,
    TouristSessionSerializer,
    TouristRegisterSerializer,
)

__all__ = ("TouristJoinView", "TouristRegisterView", "TouristSessionStatusView", "TouristLeaveView")


class TouristRegisterView(APIView):
    """
    POST /api/v1/tour/register/

    Турист нажал «продолжить» после правил.
    Создаёт TouristSession с уникальным device_token.
    """

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Определяем IP клиента
        ip = (
            request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
            or request.META.get("REMOTE_ADDR")
        )
        device_name = (request.data.get("device_name") or "").strip()

        token = _next_device_token()
        tourist = TouristSession.objects.create(
            device_token=token,
            device_name=device_name,
            ip_address=ip or None,
        )
        return Response(
            TouristRegisterSerializer(tourist).data,
            status=status.HTTP_201_CREATED,
        )


class TouristJoinView(APIView):
    """
    POST /api/v1/tour/join/

    Турист подключается к активной сессии специалиста по его номеру.
    Возвращает session_id для подключения по WebSocket.

    Body: {"specialist_number": 1, "device_token": "..."}
    """

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = TouristJoinSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        specialist_number = serializer.validated_data["specialist_number"]
        device_token = serializer.validated_data["device_token"]

        try:
            specialist = Specialist.objects.get(
                number=specialist_number, is_active=True
            )
        except Specialist.DoesNotExist:
            return Response(
                {"error": "Специалист не найден или неактивен"},
                status=status.HTTP_404_NOT_FOUND,
            )

        session = (
            TourSession.objects.filter(
                specialist=specialist,
                status=TourSession.Status.WAITING,
            )
            .select_related("specialist__user")
            .first()
        )

        if not session:
            return Response(
                {"error": "У специалиста нет активной сессии ожидания"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Привязываем туриста к сессии
        try:
            tourist = TouristSession.objects.get(device_token=device_token, is_active=True)
        except TouristSession.DoesNotExist:
            return Response(
                {"error": "Токен устройства не найден или неактивен"},
                status=status.HTTP_404_NOT_FOUND,
            )

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

        # Обновляем tourist_count из реального количества
        real_count = TouristSession.objects.filter(
            tour_session=session, is_active=True
        ).count()
        session.tourist_count = real_count
        session.save(update_fields=["tourist_count"])

        # Уведомляем WS-группу специалиста о новом туристе
        channel_layer = get_channel_layer()
        group_name = f"tour_{session.pk}"
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "tourist.joined",
                "tourist_count": real_count,
                "tourist_id": tourist.pk,
                "device_token": str(tourist.device_token),
            },
        )

        # Уведомляем lobby-WS туриста о назначенной сессии
        personal_lobby = f"lobby_{tourist.device_token}"
        async_to_sync(channel_layer.group_send)(
            personal_lobby,
            {
                "type": "session.assigned",
                "session_id": session.pk,
                "specialist_name": session.specialist.name,
                "specialist_number": session.specialist.number,
            },
        )

        return Response(
            TouristSessionSerializer(session).data,
            status=status.HTTP_200_OK,
        )


class TouristSessionStatusView(APIView):
    """
    GET /api/v1/tour/status/?device_token=<uuid>

    Возвращает текущую сессию туриста (если есть).
    Используется для поллинга: турист узнаёт, добавил ли его специалист.
    """

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        device_token = request.query_params.get("device_token", "").strip()
        if not device_token:
            return Response({"session_id": None, "status": None})

        try:
            tourist = TouristSession.objects.select_related("tour_session").get(
                device_token=device_token, is_active=True
            )
        except TouristSession.DoesNotExist:
            return Response({"token_valid": False, "session_id": None, "status": None})

        if not tourist.tour_session:
            return Response({"token_valid": True, "session_id": None, "status": None})

        return Response({
            "token_valid": True,
            "session_id": tourist.tour_session.pk,
            "status": tourist.tour_session.status,
        })


class TouristLeaveView(APIView):
    """
    POST /api/v1/tour/leave/

    Турист нажал "назад" или вышел из тура — отвязывает от сессии.
    Body: {"device_token": 42}
    """

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        device_token = request.data.get("device_token")
        if not device_token:
            return Response({"error": "device_token обязателен"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tourist = TouristSession.objects.select_related("tour_session").get(
                device_token=device_token, is_active=True
            )
        except TouristSession.DoesNotExist:
            return Response({"error": "Токен не найден"}, status=status.HTTP_404_NOT_FOUND)

        session = tourist.tour_session
        if not session:
            return Response({"status": "ok"})

        session_id = session.pk

        # Отвязываем туриста от сессии
        tourist.tour_session = None
        tourist.tour_number = None
        tourist.joined_at = None
        tourist.save(update_fields=["tour_session", "tour_number", "joined_at"])

        # Обновляем tourist_count
        session.tourist_count = TouristSession.objects.filter(
            tour_session=session, is_active=True
        ).count()
        session.save(update_fields=["tourist_count"])

        # Уведомляем WS группу
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"tour_{session_id}",
            {
                "type": "tourist.left",
                "tourist_count": session.tourist_count,
                "tourist_id": tourist.pk,
                "device_token": str(tourist.device_token),
            },
        )

        return Response({"status": "ok"})
