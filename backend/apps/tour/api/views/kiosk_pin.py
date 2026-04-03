from decouple import config
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from tour.models import KioskPin

KIOSK_API_TOKEN = config("KIOSK_API_TOKEN", default="")

__all__ = ("KioskPinView",)


class KioskPinView(APIView):
    """
    GET /api/v1/tour/kiosk-pin/

    Возвращает текущий 6-значный PIN для выхода из киоск-мода.
    Требует заголовок: X-Kiosk-Token: <KIOSK_API_TOKEN>
    """

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        token = request.headers.get("X-Kiosk-Token", "")
        if not KIOSK_API_TOKEN or token != KIOSK_API_TOKEN:
            return Response(
                {"detail": "Invalid kiosk token"},
                status=status.HTTP_403_FORBIDDEN,
            )

        pin = KioskPin.objects.first()
        if not pin:
            return Response(
                {"detail": "PIN not configured"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response({"code": int(str(pin.code).zfill(6))})
