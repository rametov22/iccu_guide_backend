import json
import logging
import subprocess

from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = ("GuideVideo",)

logger = logging.getLogger(__name__)


def _probe_video_duration(path):
    """Возвращает длительность видео в секундах через ffprobe, или None."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", str(path)],
            capture_output=True, text=True, timeout=10,
        )
        data = json.loads(result.stdout)
        return int(float(data["format"]["duration"]))
    except Exception as exc:
        logger.warning("ffprobe failed for %s: %s", path, exc)
        return None


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
        blank=True,
        null=True,
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

    duration_seconds = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Длительность (секунд)"),
        help_text=_("Автоматически считывается из видео при загрузке"),
    )

    class Meta:
        verbose_name = _("Видео гида")
        verbose_name_plural = _("Видео гидов")
        ordering = ["section", "order"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # После сохранения файлов считываем длительность по всем языкам
        # и берём максимум — чтобы таймер секции покрыл самое длинное видео
        durations = []
        for field_name in ("video_ru", "video_en", "video_uz", "video"):
            file_field = getattr(self, field_name, None)
            if not file_field:
                continue
            try:
                d = _probe_video_duration(file_field.path)
            except (NotImplementedError, ValueError):
                d = None
            if d:
                durations.append(d)
        if durations:
            new_duration = max(durations)
            if new_duration != self.duration_seconds:
                self.duration_seconds = new_duration
                super().save(update_fields=["duration_seconds"])

    def __str__(self):
        return f"{self.guide.name} — {self.title or f'Видео #{self.order}'}"
