from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = ("KioskPin",)


class KioskPin(models.Model):
    code = models.PositiveIntegerField(
        verbose_name=_("PIN-код"),
        help_text=_("6-значный код для выхода из киоск-мода"),
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("PIN киоска")
        verbose_name_plural = _("PIN киоска")

    def __str__(self):
        return str(self.code).zfill(6)
