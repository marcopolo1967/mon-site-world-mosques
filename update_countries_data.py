import sys
import os
import requests

sys.path.append('F:/Logiciels/Mosquee_Annuaire')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Mosquee_Annuaire.settings')

import django

django.setup()

from mosques.models import Country


def update_all_countries():
    print("Mise à jour des pays...")

    url = "https://restcountries.com/v3.1/all?fields=cca2,capital,population,currencies,flags,name"

    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
    except Exception as e:
        print("Erreur connexion API :", e)
        return

    all_countries = response.json()
    print(f"📊 {len(all_countries)} pays reçus")
    updated = 0

    for api_country in all_countries:
        code = api_country.get("cca2", "").upper()
        if not code or len(code) != 2:
            continue

        # Trouver le pays dans votre base
        country = Country.objects.filter(code=code).first()
        if not country:
            print(f"  ⚠️ {code}: non trouvé dans votre base")
            continue

        # 1. CAPITALE (en anglais seulement de l'API)
        capital = ""
        if api_country.get("capital"):
            capital = api_country["capital"][0]

        # On met en anglais (car API donne en anglais)
        country.capital_en = capital[:100]
        # Pour français/arabe, on garde ce qui existe ou on laisse vide

        # 2. POPULATION
        country.population = api_country.get("population", 0)

        # 3. DEVISE (nom anglais)
        currency_name = ""
        currencies = api_country.get("currencies")
        if currencies:
            # Premier code devise trouvé
            for curr_code, curr_data in currencies.items():
                currency_name = curr_data.get("name", "")
                break

        country.currency_en = currency_name[:50]

        # 4. DRAPEAU (URL PNG)
        flag_url = ""
        flags = api_country.get("flags")
        if flags:
            flag_url = flags.get("png", "")

        country.flag_url = flag_url[:200]

        country.save()
        updated += 1

        if updated % 20 == 0:
            print(f"  🔄 {updated} pays mis à jour...")

    print(f"\n✅ Terminé ! {updated}/{len(all_countries)} pays mis à jour")


if __name__ == "__main__":
    update_all_countries()