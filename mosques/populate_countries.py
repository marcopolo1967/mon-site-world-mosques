# mosques/populate_countries.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'votre_projet.settings')
django.setup()

from mosques.models import Country

COUNTRIES_DATA = [
    {
        'name_fr': 'Algérie',
        'name_ar': 'الجزائر',
        'name_en': 'Algeria',
        'code': 'DZ',
        'continent': 'af',
        'flag': '🇩🇿'
    },
    {
        'name_fr': 'Maroc',
        'name_ar': 'المغرب',
        'name_en': 'Morocco',
        'code': 'MA',
        'continent': 'af',
        'flag': '🇲🇦'
    },
    {
        'name_fr': 'Tunisie',
        'name_ar': 'تونس',
        'name_en': 'Tunisia',
        'code': 'TN',
        'continent': 'af',
        'flag': '🇹🇳'
    },
    {
        'name_fr': 'France',
        'name_ar': 'فرنسا',
        'name_en': 'France',
        'code': 'FR',
        'continent': 'eu',
        'flag': '🇫🇷'
    },
    {
        'name_fr': 'Turquie',
        'name_ar': 'تركيا',
        'name_en': 'Turkey',
        'code': 'TR',
        'continent': 'as',
        'flag': '🇹🇷'
    },
    # Ajoutez d'autres pays selon vos besoins
]

def populate():
    for country_data in COUNTRIES_DATA:
        country, created = Country.objects.get_or_create(
            code=country_data['code'],
            defaults=country_data
        )
        if created:
            print(f"✅ Créé : {country_data['name_fr']}")
        else:
            print(f"⚠️ Existe déjà : {country_data['name_fr']}")

if __name__ == '__main__':
    print("Peuplement de la table Country...")
    populate()
    print("Terminé !")