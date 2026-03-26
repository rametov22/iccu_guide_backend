from django.urls import path

from .. import views

__all__ = ("urlpatterns",)


urlpatterns = [
    path("specialist/me/", views.SpecialistMeView.as_view(), name="specialist-me"),
    path(
        "sessions/<int:pk>/",
        views.TourSessionDetailView.as_view(),
        name="session-detail",
    ),
    path(
        "sessions/create/",
        views.TourSessionCreateView.as_view(),
        name="session-create",
    ),
    path(
        "sessions/<int:pk>/tourists/",
        views.TourSessionTouristListView.as_view(),
        name="session-tourists",
    ),
    path(
        "sessions/<int:pk>/tourists/add/",
        views.TourSessionTouristAddView.as_view(),
        name="session-tourist-add",
    ),
    path(
        "sessions/<int:pk>/tourists/<int:tourist_id>/",
        views.TourSessionTouristKickView.as_view(),
        name="session-tourist-kick",
    ),
]
