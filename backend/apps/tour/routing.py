from django.urls import re_path

from .consumers import TourConsumer, LobbyConsumer

websocket_urlpatterns = [
    re_path(r"ws/tour/(?P<session_id>\d+)/$", TourConsumer.as_asgi()),
    re_path(r"ws/lobby/$", LobbyConsumer.as_asgi()),
]
