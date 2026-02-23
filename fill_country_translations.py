# fill_country_translations.py
import os
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Mosquee_Annuaire.settings')
django.setup()

from mosques.models import Country
from googletrans import Translator

translator = Translator()

print("=== TRADUCTION AUTOMATIQUE DES PAYS ===")

countries = Country.objects.all()
print(f"Total pays: {countries.count()}")

for country in countries:
    updated = False

    # Traduction nom français → arabe
    if country.name_fr and not country.name_ar:
        try:
            translated = translator.translate(country.name_fr, dest='ar')
            country.name_ar = translated.text
            updated = True
            print(f"  {country.name_fr} → {country.name_ar}")
            time.sleep(0.1)  # Éviter rate limiting
        except Exception as e:
            print(f"  ❌ {country.name_fr} arabe: {e}")

    # Traduction nom français → anglais
    if country.name_fr and not country.name_en:
        try:
            # Pour les noms de pays, souvent le nom anglais est similaire
            # On vérifie d'abord si besoin de traduction
            if country.name_fr.lower() not in country.name_fr.lower():
                translated = translator.translate(country.name_fr, dest='en')
                country.name_en = translated.text
            else:
                country.name_en = country.name_fr  # Garde le nom français
            updated = True
            print(f"  {country.name_fr} → {country.name_en}")
            time.sleep(0.1)
        except Exception as e:
            print(f"  ❌ {country.name_fr} anglais: {e}")

    if updated:
        country.save()

print("\n✅ Traduction terminée !")

# Vérification
empty_ar = Country.objects.filter(name_ar='').count()
empty_en = Country.objects.filter(name_en='').count()
print(f"Pays sans nom arabe: {empty_ar}")
print(f"Pays sans nom anglais: {empty_en}")