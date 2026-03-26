from decouple import config
from django.apps import apps
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

APP_NAME = settings.APP_NAME

__all__ = ("urlpatterns",)

admin_urlpatterns = []
if apps.is_installed("django.contrib.admin"):
    admin.site.site_title = _("%(app_name)s site admin") % {"app_name": APP_NAME}
    admin.site.site_header = _("%(app_name)s administration") % {"app_name": APP_NAME}
    admin.site.index_title = _("Site administration")
    admin.site.enable_nav_sidebar = True
    admin.site.empty_value_display = "-"

    admin_urlpatterns = [path("admin/", admin.site.urls)]


urlpatterns = [
    path(
        "healthcheck/",
        lambda request: JsonResponse({"status": "ok"}),
        name="healthcheck",
    ),
    path(
        "ws-test/", TemplateView.as_view(template_name="ws_test.html"), name="ws-test"
    ),
    path(
        "tourist/", TemplateView.as_view(template_name="tourist.html"), name="tourist"
    ),
    path("martor/", include("martor.urls")),
    # i18n endpoints (used by Unfold for language switcher, name: `set_language`)
    path("i18n/", include("django.conf.urls.i18n")),
]


urlpatterns += i18n_patterns(
    *admin_urlpatterns,
    path("api/v1/", include("config.api.v1.urls", namespace="api")),
)


if not config("PRODUCTION", cast=bool, default=True):
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if "rosetta" in settings.INSTALLED_APPS:
    urlpatterns += [path("rosetta/", include("rosetta.urls"))]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
