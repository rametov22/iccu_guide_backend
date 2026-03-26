from rest_framework import permissions, views
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..serializers import SpecialistProfileSerializer

__all__ = ("SpecialistMeView",)


class SpecialistMeView(views.APIView):
    """
    GET /api/specialist/me/

    Профиль текущего специалиста (по JWT токену).
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            specialist = request.user.specialist_profile
        except Exception:
            return Response(
                {"detail": "У этого пользователя нет профиля специалиста."},
                status=403,
            )
        serializer = SpecialistProfileSerializer(specialist)
        return Response(serializer.data)
