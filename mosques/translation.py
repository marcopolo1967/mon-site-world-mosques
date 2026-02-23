from modeltranslation.translator import register, TranslationOptions
from .models import Mosque, Proposition

@register(Mosque)
class MosqueTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'history')
    # Remplace empty_values par ceci :
    required_languages = []


@register(Proposition)
class PropositionTranslationOptions(TranslationOptions):
    fields = ('description', 'history')