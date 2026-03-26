from django.urls import path

from .. import views

__all__ = ("urlpatterns",)


urlpatterns = [
    path("halls/", views.HallTreeView.as_view(), name="hall-tree"),
    path(
        "sections/<int:section_id>/exhibits/",
        views.ExhibitsBySectionView.as_view(),
        name="exhibits-by-section",
    ),
]
