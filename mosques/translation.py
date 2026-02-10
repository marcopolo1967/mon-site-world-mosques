from modeltranslation.translator import register, TranslationOptions
from .models import Mosque, Proposition

@register(Mosque)
class MosqueTranslationOptions(TranslationOptions):
    fields = ('description', 'history')

@register(Proposition)
class PropositionTranslationOptions(TranslationOptions):
    fields = ('description', 'history')