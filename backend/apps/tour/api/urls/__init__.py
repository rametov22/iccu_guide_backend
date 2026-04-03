from django.urls import path

from .. import views

__all__ = ("urlpatterns",)


urlpatterns = [
    path("register/", views.TouristRegisterView.as_view(), name="tourist-register"),
    path("join/", views.TouristJoinView.as_view(), name="tourist-join"),
    path("rating/", views.TourRatingView.as_view(), name="tour-rating"),
    path("status/", views.TouristSessionStatusView.as_view(), name="tourist-status"),
    path("leave/", views.TouristLeaveView.as_view(), name="tourist-leave"),
    path("select-guide/", views.TouristSelectGuideView.as_view(), name="tourist-select-guide"),
    path("kiosk-pin/", views.KioskPinView.as_view(), name="kiosk-pin"),
]
