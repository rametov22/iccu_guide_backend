from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from ...models import Device, DeviceFileState
from ...services import build_manifest
from ..serializers import (
    DeviceAdminSerializer,
    DeviceFileStateSerializer,
    DeviceFileStateUpdateSerializer,
    DeviceRegisterSerializer,
    DeviceSerializer,
)

__all__ = (
    "DeviceRegisterView",
    "DeviceManifestView",
    "DeviceFileStatusView",
    "DeviceAdminListView",
)


class DeviceRegisterView(APIView):
    """
    POST /api/v1/devices/register/

    Фронт отправляет {onesignal_player_id, name?} при первом запуске.
    Если устройство с таким player_id уже есть — обновляет name и
    last_seen_at, статусы файлов остаются прежними. Если приложение
    переустановили, OneSignal выдаёт новый player_id → создаётся новая
    запись Device, статусы скачивания «обнуляются» сами по себе.
    """

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = DeviceRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        player_id = serializer.validated_data["onesignal_player_id"]
        name = serializer.validated_data.get("name", "")

        device, created = Device.objects.get_or_create(
            onesignal_player_id=player_id,
            defaults={"name": name},
        )
        if not created:
            updates = ["last_seen_at"]
            if name and device.name != name:
                device.name = name
                updates.append("name")
            if not device.is_active:
                device.is_active = True
                updates.append("is_active")
            device.save(update_fields=updates)

        return Response(
            DeviceSerializer(device).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class DeviceManifestView(APIView):
    """
    GET /api/v1/devices/<id>/manifest/

    Список всех файлов в системе с указанием размеров. Фронт сравнивает
    с локальным состоянием и качает то, чего нет (или что заменили).
    Также возвращает уже сохранённые статусы по этому устройству — фронт
    может пропустить файлы со status=done.
    """

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        try:
            device = Device.objects.get(pk=pk, is_active=True)
        except Device.DoesNotExist:
            return Response({"detail": "Device not found"}, status=404)

        device.save(update_fields=["last_seen_at"])

        manifest = build_manifest(request)
        states = {
            s.file_url: s for s in DeviceFileState.objects.filter(device=device)
        }

        for f in manifest["files"]:
            s = states.get(f["url"])
            if s:
                f["status"] = s.status
                f["progress"] = s.progress
            else:
                f["status"] = DeviceFileState.Status.PENDING
                f["progress"] = 0

        return Response(manifest)


class DeviceFileStatusView(APIView):
    """
    POST /api/v1/devices/<id>/file-status/

    Фронт пушит прогресс скачивания одного файла.
    Body: {file_url, status, progress?, file_size?, error_message?}
    """

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk):
        try:
            device = Device.objects.get(pk=pk, is_active=True)
        except Device.DoesNotExist:
            return Response({"detail": "Device not found"}, status=404)

        serializer = DeviceFileStateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        v = serializer.validated_data

        # Если файл уже скачан, прогресс должен быть 100
        progress = v.get("progress", 0)
        if v["status"] == DeviceFileState.Status.DONE:
            progress = 100

        state, _ = DeviceFileState.objects.update_or_create(
            device=device,
            file_url=v["file_url"],
            defaults={
                "status": v["status"],
                "progress": progress,
                "file_size": v.get("file_size", 0),
                "error_message": v.get("error_message", ""),
            },
        )
        device.save(update_fields=["last_seen_at"])
        return Response(DeviceFileStateSerializer(state).data)


class DeviceAdminListView(ListAPIView):
    """
    GET /api/v1/devices/admin/

    Список устройств для админ-дашборда: имя, время последнего контакта,
    сводка по скачиванию (всего / done / error / pending).
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAdminUser]
    serializer_class = DeviceAdminSerializer

    def get_queryset(self):
        return Device.objects.annotate(
            files_total=Count("file_states"),
            files_done=Count(
                "file_states",
                filter=Q(file_states__status=DeviceFileState.Status.DONE),
            ),
            files_error=Count(
                "file_states",
                filter=Q(file_states__status=DeviceFileState.Status.ERROR),
            ),
            files_pending=Count(
                "file_states",
                filter=Q(file_states__status__in=[
                    DeviceFileState.Status.PENDING,
                    DeviceFileState.Status.DOWNLOADING,
                ]),
            ),
        ).order_by("-last_seen_at")
