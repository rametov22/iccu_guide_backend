from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = ("TourRating",)


class TourRating(models.Model):
    """
    Оценка тура от туриста после завершения.
    """

    tourist_session = models.OneToOneField(
        "tour.TouristSession",
        on_delete=models.CASCADE,
        related_name="rating",
        verbose_name=_("Сессия туриста"),
    )

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Оценка"),
        help_text=_("От 1 до 5 звёзд"),
    )

    comment = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Комментарий"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата"),
    )

    class Meta:
        verbose_name = _("Оценка тура")
        verbose_name_plural = _("Оценки туров")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Оценка {self.rating}★ — сессия #{self.tourist_session_id}"
