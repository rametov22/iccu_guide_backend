from django.db import models
from django.utils.translation import gettext_lazy as _

from .specialist import Specialist

__all__ = ("TourSession",)


class TourSession(models.Model):
    """
    Сессия тура.
    Создаётся специалистом когда он готов принимать туристов.
    """

    class Status(models.TextChoices):
        WAITING = "waiting", _("Ожидание подключений")
        IN_PROGRESS = "in_progress", _("Тур идёт")
        ON_BREAK = "on_break", _("Перерыв")
        HALL_TRANSITION = "hall_transition", _("Переход между залами")
        FINISHED = "finished", _("Завершён")

    specialist = models.ForeignKey(
        Specialist,
        on_delete=models.CASCADE,
        related_name="sessions",
        verbose_name=_("Специалист"),
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.WAITING,
        verbose_name=_("Статус"),
    )

    current_section = models.ForeignKey(
        "exhibit.Section",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="active_sessions",
        verbose_name=_("Текущий раздел"),
        help_text=_("Раздел, который специалист сейчас показывает"),
    )

    tourist_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Кол-во туристов"),
    )

    section_started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Начало текущего раздела"),
    )

    paused_remaining_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Остаток при паузе (секунд)"),
    )

    break_remaining_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Остаток перерыва (секунд)"),
    )

    is_technical_stop = models.BooleanField(
        default=False,
        verbose_name=_("Техническая остановка"),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("Сессия тура")
        verbose_name_plural = _("Сессии туров")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Сессия #{self.pk} — {self.specialist} ({self.status})"
