from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView

from specialist.models import TourSession

__all__ = ("SpecialistLoginView", "SpecialistLogoutView")


class SpecialistLoginView(TokenObtainPairView):
    """
    POST /api/v1/users/auth/login/

    Логин + автосоздание сессии тура для специалиста.
    Если у специалиста нет незавершённой сессии — создаёт WAITING.
    """

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            from django.contrib.auth import get_user_model
            from rest_framework_simplejwt.tokens import AccessToken

            User = get_user_model()
            token = AccessToken(response.data["access"])
            user = User.objects.get(pk=token["user_id"])

            if user.is_specialist:
                specialist = user.specialist_profile

                active_session = TourSession.objects.filter(
                    specialist=specialist,
                ).exclude(
                    status=TourSession.Status.FINISHED,
                ).first()

                if active_session:
                    response.data["session_id"] = active_session.pk
                else:
                    session = TourSession.objects.create(specialist=specialist)
                    response.data["session_id"] = session.pk

                    # Уведомляем lobby о новом специалисте
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        "lobby",
                        {"type": "specialist.update"},
                    )

        return response


class SpecialistLogoutView(APIView):
    """
    POST /api/v1/users/auth/logout/

    Завершает активную сессию тура специалиста и уведомляет туристов по WS.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if not user.is_specialist:
            return Response({"detail": "Не специалист"}, status=status.HTTP_403_FORBIDDEN)

        specialist = user.specialist_profile
        session = (
            TourSession.objects.filter(specialist=specialist)
            .exclude(status=TourSession.Status.FINISHED)
            .first()
        )

        if session:
            session.status = TourSession.Status.FINISHED
            session.finished_at = timezone.now()
            session.save(update_fields=["status", "finished_at"])

            channel_layer = get_channel_layer()
            group_name = f"tour_{session.pk}"
            async_to_sync(channel_layer.group_send)(
                group_name,
                {"type": "tour.finished"},
            )

            # Уведомляем lobby о смене списка специалистов
            async_to_sync(channel_layer.group_send)(
                "lobby",
                {"type": "specialist.update"},
            )

        return Response({"status": "ok"})
