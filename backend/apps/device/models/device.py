from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = ("Device", "DeviceFileState")


class Device(models.Model):
    """
    Устройство (iPad) с подпиской на Firebase Cloud Messaging.

    Создаётся при первом запуске приложения: фронт получает
    FCM-токен через firebase_messaging и шлёт его на
    POST /api/v1/devices/register/. Если приложение переустановили —
    Firebase выдаёт новый токен, появится новая запись Device, и статус
    скачивания media сбросится сам.
    """

    fcm_token = models.CharField(
        max_length=512,
        unique=True,
        verbose_name=_("FCM token"),
    )

    name = models.CharField(
        max_length=64,
        blank=True,
        default="",
        verbose_name=_("Название"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Активно"),
    )

    last_seen_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Последний контакт"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Создано"),
    )

    class Meta:
        verbose_name = _("Устройство")
        verbose_name_plural = _("Устройства")
        ordering = ["-last_seen_at"]

    def __str__(self):
        label = self.name or self.fcm_token[:12]
        return f"Device #{self.pk} · {label}"


class DeviceFileState(models.Model):
    """
    Статус скачивания конкретного медиа-файла на конкретном устройстве.

    Ключ — пара (device, file_url). Когда админ заменяет файл, у нового
    URL появляется новая запись, старая остаётся как история (или может
    быть очищена позже).
    """

    class Status(models.TextChoices):
        PENDING = "pending", _("Ожидание")
        DOWNLOADING = "downloading", _("Скачивается")
        DONE = "done", _("Скачано")
        ERROR = "error", _("Ошибка")

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="file_states",
        verbose_name=_("Устройство"),
    )

    file_url = models.CharField(
        max_length=500,
        verbose_name=_("URL файла"),
    )

    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("Статус"),
    )

    progress = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Прогресс, %"),
        help_text=_("0..100"),
    )

    file_size = models.BigIntegerField(
        default=0,
        verbose_name=_("Размер, байт"),
    )

    error_message = models.CharField(
        max_length=500,
        blank=True,
        default="",
        verbose_name=_("Сообщение об ошибке"),
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Статус файла на устройстве")
        verbose_name_plural = _("Статусы файлов на устройствах")
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["device", "file_url"],
                name="unique_device_file",
            ),
        ]
        indexes = [
            models.Index(fields=["device", "status"]),
        ]

    def __str__(self):
        return f"{self.device_id} · {self.status} · {self.progress}%"
