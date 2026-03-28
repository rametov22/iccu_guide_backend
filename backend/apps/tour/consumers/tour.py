import asyncio
from datetime import timedelta

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from django.utils import timezone

from specialist.models import TourSession
from tour.models import TouristSession

MEDIA_URL = getattr(settings, "MEDIA_URL", "/media/")

__all__ = ("TourConsumer",)


class TourConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket для управления туром.

    Подключение:
        ws/tour/{session_id}/?role=specialist
        ws/tour/{session_id}/?device_token=<uuid>
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_id = None
        self.group_name = None
        self.is_specialist = False
        self.device_token = None
        self.tourist_session = None
        self._timer_task = None

    # ── Connect / Disconnect ──────────────────────────────────

    async def connect(self):
        self.session_id = self.scope["url_route"]["kwargs"]["session_id"]
        self.group_name = f"tour_{self.session_id}"

        session = await self._get_session()
        if not session:
            await self.close(code=4004)
            return

        if session.status == TourSession.Status.FINISHED:
            await self.close(code=4010)
            return

        query_string = self.scope.get("query_string", b"").decode()
        params = dict(p.split("=", 1) for p in query_string.split("&") if "=" in p)
        self.is_specialist = params.get("role") == "specialist"
        self.device_token = params.get("device_token")

        if self.is_specialist:
            # Токен из query (?token=...) или из заголовка (Authorization: Bearer ...)
            token = params.get("token")
            if not token:
                headers = dict(self.scope.get("headers", []))
                auth = headers.get(b"authorization", b"").decode()
                if auth.lower().startswith("bearer "):
                    token = auth[7:]
            if not token:
                await self.close(code=4003)
                return
            specialist = await self._authenticate_specialist(token, session)
            if not specialist:
                await self.close(code=4003)
                return
        else:
            if not self.device_token:
                await self.close(code=4001)
                return
            tourist = await self._get_tourist_session()
            if not tourist:
                await self.close(code=4001)
                return
            self.tourist_session = tourist

        await self.channel_layer.group_add(self.group_name, self.channel_name)

        if not self.is_specialist and self.device_token:
            self.personal_group = f"tourist_{self.device_token}"
            await self.channel_layer.group_add(self.personal_group, self.channel_name)

        await self.accept()

        # Отправляем текущее состояние
        state = await self._get_session_state()
        await self.send_json({"type": "tour_info", **state})

        # Специалист переподключается к активному туру — перезапускаем таймер
        if self.is_specialist and session.status == TourSession.Status.IN_PROGRESS:
            remaining = await self._calculate_remaining_seconds()
            if remaining and remaining > 0:
                self._start_section_timer(remaining)

    async def disconnect(self, close_code):
        if self._timer_task:
            self._cancel_timer()

        if self.group_name:
            if not self.is_specialist:
                count = await self._decrement_tourist_count()
                await self.channel_layer.group_send(
                    self.group_name,
                    {"type": "tourist.left", "tourist_count": count},
                )
                if hasattr(self, "personal_group"):
                    await self.channel_layer.group_discard(
                        self.personal_group, self.channel_name
                    )

            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # ── Receive commands ──────────────────────────────────────

    async def receive_json(self, content, **kwargs):
        if not self.is_specialist:
            return

        action = content.get("action")

        if action == "start_tour":
            result = await self._do_start_tour()
            if result:
                duration, state = result
                await self.channel_layer.group_send(
                    self.group_name,
                    {"type": "tour.info", **state},
                )
                self._start_section_timer(duration)

        elif action == "next_section":
            self._cancel_timer()
            result = await self._do_next_section()
            if result is None:
                await self._do_finish_tour()
                await self.channel_layer.group_send(
                    self.group_name,
                    {"type": "tour.finished"},
                )
            else:
                duration, state = result
                await self.channel_layer.group_send(
                    self.group_name,
                    {"type": "tour.info", **state},
                )
                self._start_section_timer(duration)

        elif action == "prev_section":
            self._cancel_timer()
            result = await self._do_prev_section()
            if result:
                duration, state = result
                await self.channel_layer.group_send(
                    self.group_name,
                    {"type": "tour.info", **state},
                )
                self._start_section_timer(duration)

        elif action == "set_break":
            await self._do_set_break(is_technical=False)
            self._cancel_timer()
            state = await self._get_session_state()
            await self.channel_layer.group_send(
                self.group_name,
                {"type": "tour.info", **state},
            )

        elif action == "technical_stop":
            await self._do_set_break(is_technical=True)
            self._cancel_timer()
            state = await self._get_session_state()
            await self.channel_layer.group_send(
                self.group_name,
                {"type": "tour.info", **state},
            )

        elif action == "resume_tour":
            result = await self._do_resume_tour()
            if result:
                remaining, state = result
                await self.channel_layer.group_send(
                    self.group_name,
                    {"type": "tour.info", **state},
                )
                self._start_section_timer(remaining)

        elif action == "finish_tour":
            self._cancel_timer()
            await self._do_finish_tour()
            await self.channel_layer.group_send(
                self.group_name,
                {"type": "tour.finished"},
            )

        elif action == "adjust_time":
            target = content.get("target")  # "section" or "break"
            delta = content.get("delta", 60)  # +60 or -60
            result = await self._do_adjust_time(target, delta)
            if result:
                state = result
                await self.channel_layer.group_send(
                    self.group_name,
                    {"type": "tour.info", **state},
                )
                if state.get("timer"):
                    remaining = state["timer"].get("section_remaining_seconds", 0)
                    if (
                        remaining > 0
                        and state.get("status") == TourSession.Status.IN_PROGRESS
                    ):
                        self._cancel_timer()
                        self._start_section_timer(remaining)

        elif action == "get_tour_info":
            info = await self._get_tour_info()
            await self.send_json({"type": "tour_info", **info})

        elif action == "kick_tourist":
            tourist_id = content.get("tourist_id")
            if tourist_id:
                await self._kick_tourist(tourist_id)

    # ── Timer management ──────────────────────────────────────

    def _start_section_timer(self, seconds):
        self._cancel_timer()
        self._timer_task = asyncio.ensure_future(self._section_timer(seconds))

    async def _section_timer(self, seconds):
        try:
            await asyncio.sleep(seconds)
            await self._auto_advance_section()
        except asyncio.CancelledError:
            pass

    def _cancel_timer(self):
        if self._timer_task and not self._timer_task.done():
            self._timer_task.cancel()
        self._timer_task = None

    async def _auto_advance_section(self):
        """Auto-break after section ends, then advance."""
        # Get break duration for current section
        break_secs = await self._get_current_break_duration()

        if break_secs and break_secs > 0:
            # Enter auto-break
            await self._do_auto_break(break_secs)
            state = await self._get_session_state()
            await self.channel_layer.group_send(
                self.group_name,
                {"type": "tour.info", **state},
            )
            # Wait for break to end, then advance
            self._timer_task = asyncio.ensure_future(
                self._break_then_advance(break_secs)
            )
        else:
            # No break — advance immediately
            await self._do_advance_or_finish()

    async def _break_then_advance(self, seconds):
        try:
            await asyncio.sleep(seconds)
            await self._do_advance_or_finish()
        except asyncio.CancelledError:
            pass

    async def _do_advance_or_finish(self):
        result = await self._do_next_section()
        if result is None:
            await self._do_finish_tour()
            await self.channel_layer.group_send(
                self.group_name,
                {"type": "tour.finished"},
            )
        else:
            duration, state = result
            await self.channel_layer.group_send(
                self.group_name,
                {"type": "tour.info", **state},
            )
            self._start_section_timer(duration)

    # ── Kick tourist ──────────────────────────────────────────

    async def _kick_tourist(self, tourist_id):
        result = await self._do_kick_tourist(tourist_id)
        if not result:
            return

        device_token, tourist_count = result

        personal_group = f"tourist_{device_token}"
        await self.channel_layer.group_send(
            personal_group,
            {"type": "tourist.kicked"},
        )

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "tourist.kicked.broadcast",
                "tourist_id": tourist_id,
                "tourist_count": tourist_count,
            },
        )

    # ── Group message handlers ────────────────────────────────

    async def tourist_joined(self, event):
        tourists = await self._get_tourists_list()
        await self.send_json(
            {
                "type": "tourist_joined",
                "tourist_count": event["tourist_count"],
                "tourist_id": event.get("tourist_id"),
                "device_token": event.get("device_token"),
                "tourists": tourists,
            }
        )

    async def tourist_left(self, event):
        tourists = await self._get_tourists_list()
        await self.send_json(
            {
                "type": "tourist_left",
                "tourist_count": event["tourist_count"],
                "tourist_id": event.get("tourist_id"),
                "device_token": event.get("device_token"),
                "tourists": tourists,
            }
        )

    async def tour_info(self, event):
        await self.send_json(
            {k: v for k, v in event.items() if k != "type"} | {"type": "tour_info"}
        )

    async def tour_finished(self, event):
        await self.send_json({"type": "tour_finished"})

    async def tourist_kicked(self, event):
        await self.send_json({"type": "kicked"})
        await self.close(code=4003)

    async def tourist_kicked_broadcast(self, event):
        tourists = await self._get_tourists_list()
        await self.send_json(
            {
                "type": "tourist_kicked",
                "tourist_id": event["tourist_id"],
                "tourist_count": event["tourist_count"],
                "tourists": tourists,
            }
        )

    # ── Shared state builder (sync, called inside @database_sync_to_async) ──

    def _build_state_dict(self, session):
        """Build session state dict. Must be called from sync context (inside @database_sync_to_async)."""
        from exhibit.models import Section

        section_data = None
        hall_data = None
        timer_data = None

        if session.current_section:
            sec = session.current_section
            section_data = {
                "id": sec.id,
                "name": str(sec.name),
                "duration_minutes": sec.duration_minutes,
                "break_duration_minutes": sec.break_duration_minutes,
            }
            hall_data = {
                "id": sec.hall.id,
                "name": str(sec.hall.name),
            }

            if (
                session.status == TourSession.Status.IN_PROGRESS
                and session.section_started_at
            ):
                now = timezone.now()
                elapsed = (now - session.section_started_at).total_seconds()
                section_total = sec.duration_minutes * 60
                remaining = max(0, section_total - elapsed)
                timer_data = {
                    "section_remaining_seconds": int(remaining),
                    "section_total_seconds": section_total,
                }
            elif (
                session.status == TourSession.Status.ON_BREAK
                and session.paused_remaining_seconds is not None
            ):
                timer_data = {
                    "section_remaining_seconds": session.paused_remaining_seconds,
                    "section_total_seconds": sec.duration_minutes * 60,
                }

        total_remaining = self._calc_total_remaining(session, timer_data)

        all_sections = list(
            Section.objects.filter(is_active=True)
            .order_by("hall__order", "order")
            .select_related("hall")
        )
        total_sections_count = len(all_sections)
        total_tour_seconds = sum(
            (s.duration_minutes + s.break_duration_minutes) * 60 for s in all_sections
        )

        # Разделы текущего зала
        hall_sections = []
        if hall_data:
            for s in all_sections:
                if s.hall_id == hall_data["id"]:
                    hall_sections.append({
                        "id": s.id,
                        "name": str(s.name),
                        "duration_minutes": s.duration_minutes,
                        "break_duration_minutes": s.break_duration_minutes,
                    })

        tourist_count = TouristSession.objects.filter(
            tour_session=session, is_active=True
        ).count()

        is_auto_break = (
            session.status == TourSession.Status.ON_BREAK
            and not session.is_technical_stop
            and session.paused_remaining_seconds is None
            and session.break_remaining_seconds
        )

        return {
            "session_id": session.pk,
            "status": session.status,
            "tourist_count": tourist_count,
            "current_section": section_data,
            "current_hall": hall_data,
            "timer": timer_data,
            "total_remaining_seconds": total_remaining,
            "total_tour_seconds": total_tour_seconds,
            "total_sections_count": total_sections_count,
            "hall_sections": hall_sections,
            "is_technical_stop": session.is_technical_stop,
            "is_auto_break": bool(is_auto_break),
            "break_remaining_seconds": (
                session.break_remaining_seconds if is_auto_break else None
            ),
        }

    def _calc_total_remaining(self, session, timer_data):
        if not session.current_section or session.status == TourSession.Status.FINISHED:
            return 0

        from exhibit.models import Section

        current_remaining = 0
        if timer_data:
            current_remaining = timer_data.get("section_remaining_seconds", 0)

        all_sections = list(
            Section.objects.filter(is_active=True)
            .order_by("hall__order", "order")
            .values_list("id", "duration_minutes", "break_duration_minutes")
        )

        found_current = False
        future_seconds = 0
        for sid, dur, brk in all_sections:
            if sid == session.current_section_id:
                found_current = True
                continue
            if found_current:
                future_seconds += (dur + brk) * 60

        return int(current_remaining + future_seconds)

    # ── DB helpers ────────────────────────────────────────────

    @database_sync_to_async
    def _get_session(self):
        try:
            return TourSession.objects.select_related(
                "specialist__user", "current_section"
            ).get(pk=self.session_id)
        except TourSession.DoesNotExist:
            return None

    @database_sync_to_async
    def _authenticate_specialist(self, token, session):
        """Проверяет JWT токен и что специалист владеет этой сессией."""
        from rest_framework_simplejwt.tokens import AccessToken
        from rest_framework_simplejwt.exceptions import TokenError
        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            access = AccessToken(token)
            user = User.objects.select_related("specialist_profile").get(
                pk=access["user_id"]
            )
            specialist = user.specialist_profile
            if session.specialist_id != specialist.pk:
                return None
            return specialist
        except (TokenError, User.DoesNotExist, Exception):
            return None

    @database_sync_to_async
    def _get_tourist_session(self):
        try:
            return TouristSession.objects.get(
                device_token=self.device_token, is_active=True
            )
        except TouristSession.DoesNotExist:
            return None

    @database_sync_to_async
    def _get_session_state(self):
        session = TourSession.objects.select_related(
            "specialist__user", "current_section__hall"
        ).get(pk=self.session_id)
        return self._build_state_dict(session)

    @database_sync_to_async
    def _get_tourists_list(self):
        tourists = list(
            TouristSession.objects.filter(
                tour_session_id=self.session_id, is_active=True
            )
            .order_by("tour_number")
            .values(
                "id",
                "device_token",
                "tour_number",
                "device_name",
                "ip_address",
                "joined_at",
            )
        )
        for t in tourists:
            t["device_token"] = str(t["device_token"])
            if t["joined_at"]:
                t["joined_at"] = t["joined_at"].isoformat()
        return tourists

    @database_sync_to_async
    def _decrement_tourist_count(self):
        session = TourSession.objects.get(pk=self.session_id)
        count = TouristSession.objects.filter(
            tour_session=session, is_active=True
        ).count()
        session.tourist_count = count
        session.save(update_fields=["tourist_count"])
        return count

    @database_sync_to_async
    def _get_tour_info(self):
        session = TourSession.objects.select_related(
            "specialist__user", "current_section__hall"
        ).get(pk=self.session_id)
        return self._build_state_dict(session)

    @database_sync_to_async
    def _calculate_remaining_seconds(self):
        session = TourSession.objects.select_related("current_section").get(
            pk=self.session_id
        )
        if not session.section_started_at or not session.current_section:
            return None
        elapsed = (timezone.now() - session.section_started_at).total_seconds()
        total = session.current_section.duration_minutes * 60
        return max(0, int(total - elapsed))

    @database_sync_to_async
    def _get_current_break_duration(self):
        session = TourSession.objects.select_related("current_section").get(
            pk=self.session_id
        )
        if session.current_section:
            return session.current_section.break_duration_minutes * 60
        return 0

    # ── Combined DB operations (mutation + state in one call) ──

    @database_sync_to_async
    def _do_start_tour(self):
        from exhibit.models import Section

        session = TourSession.objects.select_related("specialist__user").get(
            pk=self.session_id
        )

        first_section = (
            Section.objects.filter(is_active=True)
            .select_related("hall")
            .order_by("hall__order", "order")
            .first()
        )
        if not first_section:
            return None

        now = timezone.now()
        session.status = TourSession.Status.IN_PROGRESS
        session.started_at = now
        session.current_section = first_section
        session.section_started_at = now
        session.paused_remaining_seconds = None
        session.is_technical_stop = False
        session.save(
            update_fields=[
                "status",
                "started_at",
                "current_section",
                "section_started_at",
                "paused_remaining_seconds",
                "is_technical_stop",
            ]
        )

        # Re-fetch with section hall for state builder
        session = TourSession.objects.select_related(
            "specialist__user", "current_section__hall"
        ).get(pk=self.session_id)

        state = self._build_state_dict(session)
        duration = first_section.duration_minutes * 60
        return duration, state

    @database_sync_to_async
    def _do_next_section(self):
        from exhibit.models import Section

        session = TourSession.objects.select_related(
            "specialist__user", "current_section__hall"
        ).get(pk=self.session_id)
        current = session.current_section
        if not current:
            return None

        all_sections = list(
            Section.objects.filter(is_active=True)
            .select_related("hall")
            .order_by("hall__order", "order")
        )

        found = False
        next_section = None
        for sec in all_sections:
            if found:
                next_section = sec
                break
            if sec.id == current.id:
                found = True

        if not next_section:
            return None

        now = timezone.now()
        session.current_section = next_section
        session.section_started_at = now
        session.status = TourSession.Status.IN_PROGRESS
        session.paused_remaining_seconds = None
        session.is_technical_stop = False
        session.save(
            update_fields=[
                "current_section",
                "section_started_at",
                "status",
                "paused_remaining_seconds",
                "is_technical_stop",
            ]
        )

        session = TourSession.objects.select_related(
            "specialist__user", "current_section__hall"
        ).get(pk=self.session_id)

        state = self._build_state_dict(session)
        duration = next_section.duration_minutes * 60
        return duration, state

    @database_sync_to_async
    def _do_prev_section(self):
        from exhibit.models import Section

        session = TourSession.objects.select_related(
            "specialist__user", "current_section__hall"
        ).get(pk=self.session_id)
        current = session.current_section
        if not current:
            return None

        all_sections = list(
            Section.objects.filter(is_active=True)
            .select_related("hall")
            .order_by("hall__order", "order")
        )

        prev_section = None
        for sec in all_sections:
            if sec.id == current.id:
                break
            prev_section = sec

        if not prev_section:
            return None

        now = timezone.now()
        session.current_section = prev_section
        session.section_started_at = now
        session.status = TourSession.Status.IN_PROGRESS
        session.paused_remaining_seconds = None
        session.is_technical_stop = False
        session.save(
            update_fields=[
                "current_section",
                "section_started_at",
                "status",
                "paused_remaining_seconds",
                "is_technical_stop",
            ]
        )

        session = TourSession.objects.select_related(
            "specialist__user", "current_section__hall"
        ).get(pk=self.session_id)

        state = self._build_state_dict(session)
        duration = prev_section.duration_minutes * 60
        return duration, state

    @database_sync_to_async
    def _do_set_break(self, is_technical=False):
        session = TourSession.objects.select_related("current_section").get(
            pk=self.session_id
        )
        now = timezone.now()

        remaining = 0
        if session.section_started_at and session.current_section:
            elapsed = (now - session.section_started_at).total_seconds()
            total = session.current_section.duration_minutes * 60
            remaining = max(0, int(total - elapsed))

        session.status = TourSession.Status.ON_BREAK
        session.paused_remaining_seconds = remaining
        session.is_technical_stop = is_technical
        session.save(
            update_fields=["status", "paused_remaining_seconds", "is_technical_stop"]
        )
        return remaining

    @database_sync_to_async
    def _do_auto_break(self, break_secs):
        session = TourSession.objects.get(pk=self.session_id)
        session.status = TourSession.Status.ON_BREAK
        session.break_remaining_seconds = break_secs
        session.is_technical_stop = False
        session.save(
            update_fields=["status", "break_remaining_seconds", "is_technical_stop"]
        )

    @database_sync_to_async
    def _do_resume_tour(self):
        session = TourSession.objects.select_related(
            "specialist__user", "current_section__hall"
        ).get(pk=self.session_id)
        remaining = session.paused_remaining_seconds or 0

        now = timezone.now()
        session.status = TourSession.Status.IN_PROGRESS
        elapsed = (
            (session.current_section.duration_minutes * 60 - remaining)
            if session.current_section
            else 0
        )
        session.section_started_at = now - timedelta(seconds=elapsed)
        session.paused_remaining_seconds = None
        session.break_remaining_seconds = None
        session.is_technical_stop = False
        session.save(
            update_fields=[
                "status",
                "section_started_at",
                "paused_remaining_seconds",
                "break_remaining_seconds",
                "is_technical_stop",
            ]
        )

        state = self._build_state_dict(session)
        return remaining, state

    @database_sync_to_async
    def _do_adjust_time(self, target, delta_seconds):
        """Adjust section or break duration. delta_seconds can be positive or negative."""
        from exhibit.models import Section

        session = TourSession.objects.select_related(
            "specialist__user", "current_section__hall"
        ).get(pk=self.session_id)

        if not session.current_section:
            return None

        sec = Section.objects.get(pk=session.current_section_id)

        if target == "section":
            new_dur = max(1, sec.duration_minutes + (delta_seconds // 60))
            sec.duration_minutes = new_dur
            sec.save(update_fields=["duration_minutes"])

            # Recalculate section_started_at to adjust remaining time
            if (
                session.status == TourSession.Status.IN_PROGRESS
                and session.section_started_at
            ):
                now = timezone.now()
                elapsed = (now - session.section_started_at).total_seconds()
                new_total = new_dur * 60
                new_remaining = max(0, new_total - elapsed)
                # No need to change section_started_at, timer will use new duration

        elif target == "break":
            new_brk = max(0, sec.break_duration_minutes + (delta_seconds // 60))
            sec.break_duration_minutes = new_brk
            sec.save(update_fields=["break_duration_minutes"])

        # Re-fetch and build state
        session = TourSession.objects.select_related(
            "specialist__user", "current_section__hall"
        ).get(pk=self.session_id)
        return self._build_state_dict(session)

    @database_sync_to_async
    def _do_finish_tour(self):
        session = TourSession.objects.get(pk=self.session_id)
        session.status = TourSession.Status.FINISHED
        session.finished_at = timezone.now()
        session.save(update_fields=["status", "finished_at"])

    @database_sync_to_async
    def _do_kick_tourist(self, tourist_id):
        try:
            tourist = TouristSession.objects.get(
                pk=tourist_id, tour_session_id=self.session_id, is_active=True
            )
        except TouristSession.DoesNotExist:
            return None

        # Отвязываем от сессии — турист возвращается в лобби
        tourist.tour_session = None
        tourist.tour_number = None
        tourist.joined_at = None
        tourist.save(update_fields=["tour_session", "tour_number", "joined_at"])

        session = TourSession.objects.get(pk=self.session_id)
        count = TouristSession.objects.filter(
            tour_session=session, is_active=True
        ).count()
        session.tourist_count = count
        session.save(update_fields=["tourist_count"])

        return str(tourist.device_token), count
