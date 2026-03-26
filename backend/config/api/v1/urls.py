from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

app_name = "v1"


# SWAGGER
urlpatterns = [
    path(
        "schema/",
        SpectacularAPIView.as_view(),
        name="api-schema-v1",
    ),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="api:api-schema-v1"),
        name="api-swagger-v1",
    ),
    path(
        "schema/redoc/",
        SpectacularRedocView.as_view(url_name="api:api-schema-v1"),
        name="api-redoc-v1",
    ),
]


# BASE
urlpatterns += [
    path(
        "guide/",
        include("guide.api.urls"),
    ),
    path(
        "specialist/",
        include("specialist.api.urls"),
    ),
    path(
        "exhibits/",
        include("exhibit.api.urls"),
    ),
    path(
        "tour/",
        include("tour.api.urls"),
    ),
    path(
        "users/",
        include("users.api.urls"),
    ),
]
