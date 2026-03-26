from django.urls import path

from .. import views

__all__ = ("urlpatterns",)


urlpatterns = [
    path("rules/", views.RuleApiView.as_view(), name="rule-list"),
    path("specialists/", views.SpecialistListView.as_view(), name="specialist-list"),
    path("guides/", views.GuideListView.as_view(), name="guide-list"),
    path("backgrounds/", views.BackgroundListView.as_view(), name="background-list"),
]
