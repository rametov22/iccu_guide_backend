from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = ("Guide",)


class Guide(models.Model):
    """
    Виртуальный гид — статичная модель с видео и описанием.
    Турист выбирает гида перед подключением к туру.
    """

    name = models.CharField(
        max_length=255,
        verbose_name=_("Имя"),
    )

    subtitles = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Субтитры"),
        help_text=_("Текст субтитров для видео гида"),
    )

    video = models.FileField(
        upload_to="guides/videos/",
        blank=True,
        null=True,
        verbose_name=_("Видео"),
    )

    thumbnail = models.ImageField(
        upload_to="guides/thumbnails/",
        blank=True,
        null=True,
        verbose_name=_("Превью"),
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Порядок"),
    )

    is_sign_language = models.BooleanField(
        default=False,
        verbose_name=_("Жестовый язык"),
        help_text=_("Гид показывает жестами и говорит"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Активен"),
    )

    class Meta:
        verbose_name = _("Гид")
        verbose_name_plural = _("Гиды")
        ordering = ["order", "name"]

    def __str__(self):
        return self.name
