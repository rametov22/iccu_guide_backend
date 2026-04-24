from modeltranslation.translator import TranslationOptions, register

from ..models import GuideHallVideo

__all__ = ("GuideHallVideoTranslationOptions",)


@register(GuideHallVideo)
class GuideHallVideoTranslationOptions(TranslationOptions):
    fields = ("video",)
