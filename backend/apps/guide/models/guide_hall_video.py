from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = ("GuideHallVideo",)


class GuideHallVideo(models.Model):
    """
    Видео гида для перехода между залами.
    Играет при hall_transition при заходе в этот зал.
    """

    guide = models.ForeignKey(
        "guide.Guide",
        on_delete=models.CASCADE,
        related_name="hall_videos",
        verbose_name=_("Гид"),
    )

    hall = models.ForeignKey(
        "exhibit.Hall",
        on_delete=models.CASCADE,
        related_name="guide_videos",
        verbose_name=_("Зал"),
    )

    video = models.FileField(
        upload_to="guides/hall_transitions/",
        blank=True,
        null=True,
        verbose_name=_("Видео перехода"),
    )

    class Meta:
        verbose_name = _("Видео гида — переход между залами")
        verbose_name_plural = _("Видео гидов — переходы между залами")
        unique_together = [("guide", "hall")]

    def __str__(self):
        return f"{self.guide.name} → {self.hall.name}"
