from modeltranslation.translator import TranslationOptions, register

from ..models import Guide

__all__ = ("GuideTranslationOptions",)


@register(Guide)
class GuideTranslationOptions(TranslationOptions):
    fields = ("name",)
