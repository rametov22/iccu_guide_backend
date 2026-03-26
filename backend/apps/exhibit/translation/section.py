from modeltranslation.translator import TranslationOptions, register

from ..models import Section

__all__ = ("SectionTranslationOptions",)


@register(Section)
class SectionTranslationOptions(TranslationOptions):
    fields = ("name", "description")
