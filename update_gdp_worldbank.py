import sys
import os

sys.path.append('F:/Logiciels/Mosquee_Annuaire')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Mosquee_Annuaire.settings')

import django

django.setup()

import requests
import time
from mosques.models import Country
france = Country.objects.get(code='FR')
print(f"PIB France: {france.gdp} Md$")
algeria = Country.objects.get(code='DZ')
print(f"PIB Algérie: {algeria.gdp} Md$")

def get_worldbank_gdp():
    """
    Récupère le PIB 2023 de la Banque Mondiale
    """
    print("Connexion à l'API Banque Mondiale...")

    # Mapping codes ISO3 (Banque Mondiale) -> ISO2 (notre base)
    iso3_to_iso2 = {}
    for c in Country.objects.all():
        # Essayer de deviner l'ISO3
        iso3 = c.code.upper().ljust(3, c.code[-1] if len(c.code) == 2 else ' ')
        iso3_to_iso2[iso3[:3]] = c.code

    # API Banque Mondiale : PIB en USD courants (NY.GDP.MKTP.CD)
    url = "http://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD"
    params = {
        'format': 'json',
        'date': '2023',
        'per_page': 300
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if len(data) < 2:
            print("Erreur API")
            return

        gdp_data = data[1]  # Les données sont dans le deuxième élément
        updated = 0

        for item in gdp_data:
            if item.get('value'):
                country_code = item['country']['id']  # ISO3 code
                gdp_value = float(item['value']) / 1000000000  # Convertir en milliards

                # Convertir ISO3 -> ISO2
                if country_code in iso3_to_iso2:
                    iso2_code = iso3_to_iso2[country_code]
                    try:
                        country = Country.objects.get(code=iso2_code)
                        country.gdp = round(gdp_value, 2)
                        country.save()
                        updated += 1
                        print(f"✓ {country.name_fr}: {gdp_value:.2f} Md$")
                    except:
                        continue

        print(f"\nTerminé ! {updated} pays mis à jour.")

    except Exception as e:
        print(f"Erreur: {e}")
        print("Utilisation des valeurs par défaut...")
        set_default_gdp()


def set_default_gdp():
    """Valeurs par défaut si l'API échoue"""
    default_gdp = {
        'US': 25462, 'CN': 17963, 'JP': 4250, 'DE': 4082, 'IN': 3418,
        'GB': 3089, 'FR': 2930, 'RU': 2240, 'IT': 2186, 'CA': 2137,
        'BR': 1965, 'AU': 1693, 'KR': 1693, 'ES': 1490, 'MX': 1455,
        'ID': 1319, 'NL': 1008, 'SA': 1115, 'TR': 903, 'CH': 818,
        'PL': 688, 'SE': 599, 'BE': 585, 'TH': 512, 'NG': 477,
        'AR': 641, 'AE': 508, 'IL': 522, 'NO': 547, 'DZ': 195,
        'EG': 477, 'QA': 236, 'MA': 134, 'TN': 46, 'KW': 164,
    }

    for code, gdp in default_gdp.items():
        try:
            c = Country.objects.get(code=code)
            c.gdp = gdp
            c.save()
            print(f"✓ {c.name_fr}: {gdp} Md$")
        except:
            continue

    print(f"Valeurs par défaut appliquées.")


if __name__ == "__main__":
    #get_worldbank_gdp()
    set_default_gdp()