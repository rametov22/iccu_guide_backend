from modeltranslation.translator import TranslationOptions, register

from ..models import GuideVideo

__all__ = ("GuideVideoTranslationOptions",)


@register(GuideVideo)
class GuideVideoTranslationOptions(TranslationOptions):
    fields = ("video", "title", "subtitles")
