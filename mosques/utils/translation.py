from googletrans import Translator
from langdetect import detect

translator = Translator()


def translate_text_to_3_langs(text):
    """
    Retourne TOUJOURS les 3 langues, même si le texte est déjà dans une de ces langues
    """
    if not text:
        return {'fr': '', 'en': '', 'ar': ''}

    results = {
        'fr': '',
        'en': '',
        'ar': '',
    }

    print(f"=== DEBUG DANS translate_text_to_3_langs ===")
    print(f"Texte reçu: '{text}'")

    try:
        # Détecter la langue source
        source_lang = detect(text)

        # TOUJOURS produire les 3 versions
        # 1. Français (traduire si nécessaire)
        if source_lang != 'fr':
            print(f"Langue détectée: {source_lang}")
            results['fr'] = translator.translate(text, src=source_lang, dest='fr').text
        else:
            results['fr'] = text

        # 2. Anglais (traduire si nécessaire)
        if source_lang != 'en':
            results['en'] = translator.translate(text, src=source_lang, dest='en').text
        else:
            results['en'] = text

        # 3. Arabe (traduire si nécessaire)
        if source_lang != 'ar':
            results['ar'] = translator.translate(text, src=source_lang, dest='ar').text
        else:
            results['ar'] = text

    except Exception as e:
        # En cas d'erreur, copier le texte partout
        print(f"⚠️ Erreur traduction: {e}")
        results['fr'] = text
        results['en'] = text
        results['ar'] = text

    print(f"=== RÉSULTATS TRADUCTION ===")
    print(f"Français: {results['fr'][:50]}...")
    print(f"Anglais: {results['en'][:50]}...")
    print(f"Arabe: {results['ar'][:50]}...")

    return results