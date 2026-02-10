"""
SCRIPT POUR METTRE À JOUR LES DONNÉES PAYS DEPUIS RESTCOUNTRIES API
Remplit : noms 3 langues, capitales, devises, drapeaux, population
"""
import os
import sys
import requests
from datetime import datetime
from deep_translator import GoogleTranslator
from mosques.models import Mosque

# Configuration Django
sys.path.append('F:/Logiciels\Mosquee_Annuaire')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Mosquee_Annuaire.settings')

import django

django.setup()

from mosques.models import Country


def log(message):
    """Journalisation"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


def translate_text(text, target_lang='ar', source_lang='en'):
    """
    Traduit un texte avec Google Translate
    Retourne le texte original si erreur
    """
    if not text or len(text.strip()) < 2:
        print(f"⚠️  Texte trop court pour traduction: '{text}'")
        return text

    try:
        print(f"🔤 Tentative de traduction: '{text}' -> {target_lang}")

        # Liste de langues supportées
        if target_lang == 'ar':
            translator = GoogleTranslator(source=source_lang, target='ar')
        elif target_lang == 'fr':
            translator = GoogleTranslator(source=source_lang, target='fr')
        else:
            print(f"⚠️  Langue cible non supportée: {target_lang}")
            return text

        # Traduction
        translated = translator.translate(text)
        print(f"✅ Traduction réussie: '{text}' -> '{translated}'")

        # Vérifier que la traduction n'est pas vide
        if not translated or translated == text:
            print(f"⚠️  Traduction vide ou identique à l'original")
            return text

        return translated[:100]  # Limiter à 100 caractères

    except Exception as e:
        print(f"❌ ERREUR traduction '{text}' -> {target_lang}: {str(e)}")
        return text  # Retourner l'original en cas d'erreur

def translate_mosque_text(text, target_lang='fr'):
    if not text or len(text.strip()) < 5:
        return text
    try:
        translator = GoogleTranslator(source='auto', target=target_lang)
        return translator.translate(text)
    except:
        return text


for mosque in Mosque.objects.all():
    if mosque.description_ar and not mosque.description_fr:
        mosque.description_fr = translate_mosque_text(mosque.description_ar, 'fr')
        print(f"Traduit description: {mosque.name}")

    if mosque.history_ar and not mosque.history_fr:
        mosque.history_fr = translate_mosque_text(mosque.history_ar, 'fr')
        print(f"Traduit histoire: {mosque.name}")

    mosque.save()


def translate_currency(currency_name_en):
    """Traduction devise EN -> FR/AR (base commune)"""
    translations = {
        # Devises principales
        'Euro': {'fr': 'Euro', 'ar': 'يورو'},
        'US Dollar': {'fr': 'Dollar américain', 'ar': 'الدولار الأمريكي'},
        'British Pound': {'fr': 'Livre sterling', 'ar': 'الجنيه الإسترليني'},
        'Japanese Yen': {'fr': 'Yen japonais', 'ar': 'الين الياباني'},
        'Swiss Franc': {'fr': 'Franc suisse', 'ar': 'الفرنك السويسري'},
        'Canadian Dollar': {'fr': 'Dollar canadien', 'ar': 'الدولار الكندي'},
        'Australian Dollar': {'fr': 'Dollar australien', 'ar': 'الدولار الأسترالي'},

        # Devises arabes/musulmanes
        'Saudi Riyal': {'fr': 'Riyal saoudien', 'ar': 'الريال السعودي'},
        'United Arab Emirates Dirham': {'fr': 'Dirham des Émirats', 'ar': 'درهم إماراتي'},
        'Qatari Riyal': {'fr': 'Riyal qatari', 'ar': 'الريال القطري'},
        'Kuwaiti Dinar': {'fr': 'Dinar koweïtien', 'ar': 'دينار كويتي'},
        'Bahraini Dinar': {'fr': 'Dinar bahreïni', 'ar': 'دينار بحريني'},
        'Omani Rial': {'fr': 'Rial omanais', 'ar': 'ريال عماني'},
        'Jordanian Dinar': {'fr': 'Dinar jordanien', 'ar': 'دينار أردني'},
        'Algerian Dinar': {'fr': 'Dinar algérien', 'ar': 'دينار جزائري'},
        'Moroccan Dirham': {'fr': 'Dirham marocain', 'ar': 'درهم مغربي'},
        'Tunisian Dinar': {'fr': 'Dinar tunisien', 'ar': 'دينار تونسي'},
        'Egyptian Pound': {'fr': 'Livre égyptienne', 'ar': 'جنيه مصري'},

        # Autres devises courantes
        'Chinese Yuan': {'fr': 'Yuan chinois', 'ar': 'يوان صيني'},
        'Indian Rupee': {'fr': 'Roupie indienne', 'ar': 'روبية هندية'},
        'Russian Ruble': {'fr': 'Rouble russe', 'ar': 'روبل روسي'},
        'Turkish Lira': {'fr': 'Livre turque', 'ar': 'ليرة تركية'},
        'South Korean Won': {'fr': 'Won sud-coréen', 'ar': 'وون كوري جنوبي'},
        'Mexican Peso': {'fr': 'Peso mexicain', 'ar': 'بيزو مكسيكي'},
        'Brazilian Real': {'fr': 'Real brésilien', 'ar': 'ريال برازيلي'},
        'Argentine Peso': {'fr': 'Peso argentin', 'ar': 'بيزو أرجنتيني'},
        'South African Rand': {'fr': 'Rand sud-africain', 'ar': 'راند جنوب أفريقي'},

        # Fallback générique
        'Dollar': {'fr': 'Dollar', 'ar': 'دولار'},
        'Pound': {'fr': 'Livre', 'ar': 'جنيه'},
        'Ruble': {'fr': 'Rouble', 'ar': 'روبل'},
        'Rupee': {'fr': 'Roupie', 'ar': 'روبية'},
        'Rial': {'fr': 'Rial', 'ar': 'ريال'},
        'Dinar': {'fr': 'Dinar', 'ar': 'دينار'},
        'Dirham': {'fr': 'Dirham', 'ar': 'درهم'},
        'Franc': {'fr': 'Franc', 'ar': 'فرنك'},
        'Peso': {'fr': 'Peso', 'ar': 'بيزو'},
        'Lira': {'fr': 'Livre', 'ar': 'ليرة'},
        'Krona': {'fr': 'Couronne', 'ar': 'كرونة'},
        'Krone': {'fr': 'Couronne', 'ar': 'كرونة'},
    }

    # Chercher la traduction exacte
    for en_key, trans in translations.items():
        if en_key in currency_name_en:
            return trans['fr'], trans['ar']

    # Fallback : garder l'anglais
    return currency_name_en, currency_name_en


def update_from_restcountries():
    """Fonction principale"""
    log("🌐 Connexion à REST Countries API...")

    try:
        # Récupérer TOUTES les données en une requête
        fields = [
            'cca2', 'name', 'capital', 'currencies',
            'population', 'flags', 'translations', 'languages'
        ]
        url = f"https://restcountries.com/v3.1/all?fields={','.join(fields)}"

        response = requests.get(url, timeout=30)
        response.raise_for_status()
        api_countries = response.json()

        log(f"✅ {len(api_countries)} pays reçus de l'API")

    except Exception as e:
        log(f"❌ Erreur API: {e}")
        return

    updated = 0
    not_found = []

    # Traiter chaque pays de l'API
    for api_data in api_countries:
        code = api_data.get('cca2', '').upper()
        if not code:
            continue

        # Chercher dans notre base
        try:
            country = Country.objects.get(code=code)
        except Country.DoesNotExist:
            not_found.append(code)
            continue

        # === NOMS DU PAYS (3 langues) ===
        name_en = api_data['name'].get('common', '')
        translations = api_data.get('translations', {})

        country.name_en = name_en[:100]
        country.name_fr = translations.get('fra', {}).get('common', name_en)[:100]
        country.name_ar = translations.get('ara', {}).get('common', name_en)[:100]

        # === CAPITALE ===
        capital_list = api_data.get('capital', [])
        if capital_list:
            capital_en = capital_list[0]
            country.capital_en = capital_en[:100]

            # TRADUCTION AUTOMATIQUE POUR FRANÇAIS ET ARABE
            # 1. Traduction française
            if capital_en and len(capital_en) > 1:
                capital_fr = translate_text(capital_en, target_lang='fr', source_lang='en')
                country.capital_fr = capital_fr[:100]
                log(f"    Traduction FR: {capital_en} -> {capital_fr}")
            else:
                country.capital_fr = capital_en[:100] if capital_en else ""

            # 2. Traduction arabe
            if capital_en and len(capital_en) > 1:
                capital_ar = translate_text(capital_en, target_lang='ar', source_lang='en')
                country.capital_ar = capital_ar[:100]
                log(f"    Traduction AR: {capital_en} -> {capital_ar}")
            else:
                country.capital_ar = capital_en[:100] if capital_en else ""

        # === POPULATION ===
        country.population = api_data.get('population', 0)

        # === DEVISE ===
        currencies = api_data.get('currencies', {})
        if currencies:
            # Prendre la première devise
            first_currency = list(currencies.values())[0]
            currency_en = first_currency.get('name', '')

            country.currency_en = currency_en[:50]

            # TRADUCTION AUTOMATIQUE POUR FRANÇAIS ET ARABE
            # 1. Traduction française
            if currency_en and len(currency_en) > 1:
                currency_fr = translate_text(currency_en, target_lang='fr', source_lang='en')
                country.currency_fr = currency_fr[:50]
                log(f"    Devise FR: {currency_en} -> {currency_fr}")
            else:
                country.currency_fr = currency_en[:50] if currency_en else ""

            # 2. Traduction arabe
            if currency_en and len(currency_en) > 1:
                currency_ar = translate_text(currency_en, target_lang='ar', source_lang='en')
                country.currency_ar = currency_ar[:50]
                log(f"    Devise AR: {currency_en} -> {currency_ar}")
            else:
                country.currency_ar = currency_en[:50] if currency_en else ""

        # === LANGUE OFFICIELLE ===
        languages = api_data.get('languages', {})
        if languages:
            # Prendre la première langue officielle
            # L'API renvoie: {'fra': 'French', 'eng': 'English'}
            lang_codes = list(languages.values())
            if lang_codes:
                language_en = lang_codes[0]  # Ex: "French"
                country.language_en = language_en[:100]

                # TRADUCTION AUTOMATIQUE
                # 1. Traduction française
                if language_en and len(language_en) > 1:
                    language_fr = translate_text(language_en, target_lang='fr', source_lang='en')
                    country.language_fr = language_fr[:100]
                    log(f"    Langue FR: {language_en} -> {language_fr}")
                else:
                    country.language_fr = language_en[:100] if language_en else ""

                # 2. Traduction arabe
                if language_en and len(language_en) > 1:
                    language_ar = translate_text(language_en, target_lang='ar', source_lang='en')
                    country.language_ar = language_ar[:100]
                    log(f"    Langue AR: {language_en} -> {language_ar}")
                else:
                    country.language_ar = language_en[:100] if language_en else ""


        # === DRAPEAU (URL) ===
        flags = api_data.get('flags', {})
        if flags:
            country.flag_url = flags.get('png', '')[:200]

        # Sauvegarder
        country.save()
        updated += 1

        if updated % 25 == 0:
            log(f"  🔄 {updated} pays mis à jour...")

    # Résumé
    log("\n" + "=" * 50)
    log("📊 RÉSUMÉ MISE À JOUR")
    log(f"✅ Pays mis à jour: {updated}")
    if not_found:
        log(f"⚠️  Non trouvés dans votre base: {', '.join(not_found[:10])}{'...' if len(not_found) > 10 else ''}")

    # Afficher quelques exemples
    log("\n🔍 EXEMPLES MIS À JOUR:")
    sample_codes = ['FR', 'US', 'SA', 'MA', 'TN', 'DE', 'JP']
    for code in sample_codes:
        try:
            c = Country.objects.get(code=code)
            log(f"  {code}: {c.name_fr}")
            log(f"    Capitale: {c.capital_fr or c.capital_en or 'N/A'}")
            log(f"    Devise: {c.currency_fr or c.currency_en or 'N/A'}")
            log(f"    Population: {c.population:,}")
        except:
            pass


def fill_missing_gdp():
    """Remplir PIB manquant avec valeurs par défaut"""
    log("\n💰 Remplissage PIB manquant...")

    default_gdp = {
        'US': 25462, 'CN': 17963, 'JP': 4250, 'DE': 4082, 'IN': 3418,
        'GB': 3089, 'FR': 2930, 'IT': 2186, 'CA': 2137, 'BR': 1965,
        'AU': 1693, 'KR': 1693, 'ES': 1490, 'MX': 1455, 'ID': 1319,
        'NL': 1008, 'SA': 1115, 'TR': 903, 'CH': 818, 'PL': 688,
        'SE': 599, 'BE': 585, 'TH': 512, 'NG': 477, 'AR': 641,
        'AE': 508, 'IL': 522, 'NO': 547, 'DZ': 191, 'EG': 477,
        'QA': 236, 'MA': 134, 'TN': 46, 'KW': 164, 'PE': 264,
        'MY': 407, 'SG': 466, 'BD': 460, 'ZA': 406, 'VN': 408,
        'PK': 338, 'CL': 344, 'RO': 350, 'CZ': 330, 'FI': 302,
        'PT': 260, 'GR': 222, 'DK': 400, 'IE': 530, 'CO': 344,
        'PH': 404, 'HK': 383, 'NZ': 247, 'IQ': 264, 'RU': 2240,
    }

    gdp_updated = 0
    for code, gdp_value in default_gdp.items():
        try:
            country = Country.objects.get(code=code)
            if not country.gdp or country.gdp == 0:
                country.gdp = gdp_value
                country.save()
                gdp_updated += 1
        except Country.DoesNotExist:
            continue

    log(f"✅ {gdp_updated} PIB mis à jour")


if __name__ == "__main__":
    log("=" * 60)
    log("SCRIPT DE MISE À JOUR COMPLÈTE DES DONNÉES PAYS")
    log("=" * 60)

    # 1. Mettre à jour depuis API
    update_from_restcountries()

    # 2. Remplir PIB manquant
    fill_missing_gdp()

    # 3. Vérification finale
    log("\n🎉 SCRIPT TERMINÉ AVEC SUCCÈS !")
    log("💡 Prochaines étapes:")
    log("1. Vérifiez l'admin: /admin/mosques/country/")
    log("2. Testez: /fr/panorama/pays/FR/")
    log("3. Testez: /ar/panorama/pays/SA/")
    log("4. Les capitales/devises manquantes afficheront la version anglaise")