from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from tour.models import TouristSession

__all__ = ("LobbyConsumer",)

LOBBY_GROUP = "lobby"


class LobbyConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket для лобби туриста.

    Подключение: ws/lobby/?device_token=<uuid>

    Отправляет:
      - specialist_list: обновлённый список специалистов с WAITING-сессиями
      - session_assigned: турист добавлен в сессию специалиста
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.device_token = None
        self.personal_group = None
        self._base_url = ""

    async def connect(self):
        query_string = self.scope.get("query_string", b"").decode()
        params = dict(p.split("=", 1) for p in query_string.split("&") if "=" in p)
        self.device_token = params.get("device_token")

        if not self.device_token:
            await self.close(code=4001)
            return

        tourist = await self._get_tourist()
        if not tourist:
            await self.close(code=4001)
            return

        headers = dict(self.scope.get("headers", []))
        host = headers.get(b"host", b"").decode()
        scheme = "https" if headers.get(b"x-forwarded-proto", b"").decode() == "https" else "http"
        self._base_url = f"{scheme}://{host}" if host else ""

        await self.channel_layer.group_add(LOBBY_GROUP, self.channel_name)

        self.personal_group = f"lobby_{self.device_token}"
        await self.channel_layer.group_add(self.personal_group, self.channel_name)

        await self.accept()

        # Send initial specialist list
        specialists = await self._get_specialists()
        await self.send_json({"type": "specialist_list", "specialists": specialists})

        # Check if already assigned to a session
        session_info = await self._get_session_info()
        if session_info:
            await self.send_json({"type": "session_assigned", **session_info})

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(LOBBY_GROUP, self.channel_name)
        if self.personal_group:
            await self.channel_layer.group_discard(self.personal_group, self.channel_name)

    # ── Group message handlers ───────────────────────────

    async def specialist_update(self, event):
        """Broadcast: specialist list changed."""
        specialists = await self._get_specialists()
        await self.send_json({"type": "specialist_list", "specialists": specialists})

    async def session_assigned(self, event):
        """Personal: tourist was added to a session."""
        await self.send_json({
            "type": "session_assigned",
            "session_id": event["session_id"],
            "specialist_name": event.get("specialist_name", ""),
            "specialist_number": event.get("specialist_number"),
        })

    # ── DB helpers ───────────────────────────────────────

    @database_sync_to_async
    def _get_tourist(self):
        try:
            return TouristSession.objects.get(
                device_token=self.device_token, is_active=True
            )
        except TouristSession.DoesNotExist:
            return None

    @database_sync_to_async
    def _get_specialists(self):
        base_url = self._base_url
        from specialist.models import Specialist, TourSession

        specialists = (
            Specialist.objects.filter(
                is_active=True,
                sessions__status=TourSession.Status.WAITING,
            )
            .select_related("user")
            .prefetch_related("sessions")
            .distinct()
        )

        result = []
        for s in specialists:
            session = s.sessions.filter(status=TourSession.Status.WAITING).first()
            avatar_url = f"{base_url}{s.avatar.url}" if s.avatar else None
            result.append({
                "id": s.id,
                "name": s.name,
                "number": s.number,
                "avatar": avatar_url,
                "active_session_id": session.pk if session else None,
            })
        return result

    @database_sync_to_async
    def _get_session_info(self):
        try:
            tourist = TouristSession.objects.select_related(
                "tour_session__specialist"
            ).get(device_token=self.device_token, is_active=True)
        except TouristSession.DoesNotExist:
            return None

        if not tourist.tour_session:
            return None

        return {
            "session_id": tourist.tour_session.pk,
            "specialist_name": tourist.tour_session.specialist.name,
            "specialist_number": tourist.tour_session.specialist.number,
        }
