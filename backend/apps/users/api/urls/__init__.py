from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from ..views import SpecialistLoginView, SpecialistLogoutView

__all__ = "urlpatterns"


urlpatterns = [
    path("auth/login/", SpecialistLoginView.as_view(), name="token-obtain"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/logout/", SpecialistLogoutView.as_view(), name="token-logout"),
]
