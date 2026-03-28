from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = ("GuideVideo",)


class GuideVideo(models.Model):
    """
    Видео гида. У каждого гида может быть несколько видео,
    которые воспроизводятся по очереди (по полю order).
    """

    guide = models.ForeignKey(
        "guide.Guide",
        on_delete=models.CASCADE,
        related_name="videos",
        verbose_name=_("Гид"),
    )

    section = models.ForeignKey(
        "exhibit.Section",
        on_delete=models.CASCADE,
        related_name="guide_videos",
        verbose_name=_("Раздел"),
    )

    video = models.FileField(
        upload_to="guides/videos/",
        verbose_name=_("Видео"),
    )

    subtitles = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Субтитры"),
    )

    title = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Название"),
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Порядок воспроизведения"),
    )

    class Meta:
        verbose_name = _("Видео гида")
        verbose_name_plural = _("Видео гидов")
        ordering = ["section", "order"]

    def __str__(self):
        return f"{self.guide.name} — {self.title or f'Видео #{self.order}'}"
