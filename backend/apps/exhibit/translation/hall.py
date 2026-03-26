from modeltranslation.translator import TranslationOptions, register

from ..models import Hall

__all__ = ("HallTranslationOptions",)


@register(Hall)
class HallTranslationOptions(TranslationOptions):
    fields = ("name", "description")
