from modeltranslation.translator import TranslationOptions, register

from ..models import Exhibit

__all__ = ("ExhibitTranslationOptions",)


@register(Exhibit)
class ExhibitTranslationOptions(TranslationOptions):
    fields = ("title", "description", "video")
