from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from martor.models import MartorField

__all__ = ("Rule",)


class Rule(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name=_("Заголовок"),
        help_text=_("Например: Общие правила"),
    )

    number = models.PositiveIntegerField(
        verbose_name=_("Номер блока"), help_text=_("Порядковый номер (1, 2, 3...)")
    )

    content = MartorField(
        verbose_name=_("Содержимое (Markdown)"),
        help_text=_(
            "Поддерживает markdown-разметку:\n"
            "- Списки с точками\n"
            "**Жирный текст**\n"
            "*Курсив*\n"
            "Обычный текст"
        ),
    )

    is_active = models.BooleanField(default=True, verbose_name=_("Активна"))

    class Meta:
        verbose_name = _("Блок правил")
        verbose_name_plural = _("Блоки правил")
        ordering = ["number"]

    def __str__(self):
        return f"{self.number}. {self.title}"

    def clean(self):
        if self.is_active:
            qs = Rule.objects.filter(is_active=True)

            if self.pk:
                qs = qs.exclude(pk=self.pk)

            if qs.count() >= 4:
                raise ValidationError(_("Можно иметь максимум 4 записей правил"))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
