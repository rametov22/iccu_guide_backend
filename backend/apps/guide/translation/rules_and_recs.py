from modeltranslation.translator import TranslationOptions, register

from ..models import Rule

__all__ = ("RuleTranslationOptions",)


@register(Rule)
class RuleTranslationOptions(TranslationOptions):
    fields = ("title", "content")
