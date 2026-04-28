from django.urls import path

from .. import views

__all__ = ("urlpatterns",)


urlpatterns = [
    path("register/", views.DeviceRegisterView.as_view(), name="device-register"),
    path("<int:pk>/manifest/", views.DeviceManifestView.as_view(), name="device-manifest"),
    path("<int:pk>/file-status/", views.DeviceFileStatusView.as_view(), name="device-file-status"),
    path("admin/", views.DeviceAdminListView.as_view(), name="device-admin-list"),
]
