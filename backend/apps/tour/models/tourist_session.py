from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = ("TouristSession",)

MAX_DEVICE_NUMBER = 600


def _next_device_token():
    """Выдаёт следующий свободный номер 1..600 по кругу."""
    used = set(
        TouristSession.objects.values_list("device_token", flat=True)
    )
    for n in range(1, MAX_DEVICE_NUMBER + 1):
        if n not in used:
            return n
    # Все 600 заняты — fallback
    return 1


class TouristSession(models.Model):
    """
    Сессия туриста — привязана к конкретному устройству (iPad).
    """

    tour_session = models.ForeignKey(
        "specialist.TourSession",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="tourist_sessions",
        verbose_name=_("Сессия тура"),
    )

    guide = models.ForeignKey(
        "guide.Guide",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tourist_sessions",
        verbose_name=_("Выбранный гид"),
    )

    device_token = models.PositiveIntegerField(
        unique=True,
        verbose_name=_("Номер устройства"),
        help_text=_("Число от 1 до 600"),
    )

    device_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Название устройства"),
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("IP-адрес"),
    )

    tour_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Номер в туре"),
        help_text=_("Порядковый номер присоединения к туру"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Активен"),
    )

    joined_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Присоединился"),
    )

    left_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Покинул"),
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Сессия туриста")
        verbose_name_plural = _("Сессии туристов")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Tourist #{self.device_token} ({'active' if self.is_active else 'inactive'})"
