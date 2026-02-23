import sys
import os

# Configuration Django
sys.path.append('F:/Logiciels/Mosquee_Annuaire')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Mosquee_Annuaire.settings')

import django
django.setup()

from mosques.models import Country

# Dictionnaire de traduction FR
CAPITALS_FR = {
    'Algiers': 'Alger', 'Paris': 'Paris', 'Rabat': 'Rabat', 'Tunis': 'Tunis',
    'Berlin': 'Berlin', 'London': 'Londres', 'Rome': 'Rome', 'Madrid': 'Madrid',
    'Lisbon': 'Lisbonne', 'Amsterdam': 'Amsterdam', 'Brussels': 'Bruxelles',
    'Vienna': 'Vienne', 'Bern': 'Berne', 'Oslo': 'Oslo', 'Stockholm': 'Stockholm',
    'Helsinki': 'Helsinki', 'Copenhagen': 'Copenhague', 'Warsaw': 'Varsovie',
    'Prague': 'Prague', 'Budapest': 'Budapest', 'Bucharest': 'Bucarest',
    'Sofia': 'Sofia', 'Athens': 'Athènes', 'Ankara': 'Ankara', 'Tehran': 'Téhéran',
    'Cairo': 'Le Caire', 'Riyadh': 'Riyad', 'Abu Dhabi': 'Abou Dabi',
    'Doha': 'Doha', 'Kuwait City': 'Koweït', 'Muscat': 'Mascate',
    'Manama': 'Manama', 'Jerusalem': 'Jérusalem', 'Baghdad': 'Bagdad',
    'Damascus': 'Damas', 'Beirut': 'Beyrouth', 'Amman': 'Amman',
    'Khartoum': 'Khartoum', 'Tripoli': 'Tripoli', 'Tunis': 'Tunis',
    'Algiers': 'Alger', 'Rabat': 'Rabat', 'Nouakchott': 'Nouakchott',
    'Bamako': 'Bamako', 'Ouagadougou': 'Ouagadougou', 'Niamey': 'Niamey',
    'Nairobi': 'Nairobi', 'Addis Ababa': 'Addis-Abeba', 'Dakar': 'Dakar',
    'Abidjan': 'Abidjan', 'Accra': 'Accra', 'Lomé': 'Lomé',
    'Porto-Novo': 'Porto-Novo', 'Yaoundé': 'Yaoundé', 'Libreville': 'Libreville',
    'Brazzaville': 'Brazzaville', 'Kinshasa': 'Kinshasa', 'Kigali': 'Kigali',
    'Bujumbura': 'Bujumbura', 'Dar es Salaam': 'Dar es Salam', 'Lusaka': 'Lusaka',
    'Harare': 'Harare', 'Pretoria': 'Pretoria', 'Windhoek': 'Windhoek',
    'Gaborone': 'Gaborone', 'Maseru': 'Maseru', 'Mbabane': 'Mbabane',
    'Maputo': 'Maputo', 'Antananarivo': 'Antananarivo', 'Moroni': 'Moroni',
    'Victoria': 'Victoria', 'Port Louis': 'Port-Louis',
}

CURRENCIES_FR = {
    'Algerian dinar': 'Dinar algérien', 'Euro': 'Euro',
    'Moroccan dirham': 'Dirham marocain', 'Tunisian dinar': 'Dinar tunisien',
    'United States dollar': 'Dollar américain', 'Pound sterling': 'Livre sterling',
    'Swiss franc': 'Franc suisse', 'Danish krone': 'Couronne danoise',
    'Swedish krona': 'Couronne suédoise', 'Norwegian krone': 'Couronne norvégienne',
    'Polish złoty': 'Złoty polonais', 'Czech koruna': 'Couronne tchèque',
    'Hungarian forint': 'Forint hongrois', 'Romanian leu': 'Leu roumain',
    'Bulgarian lev': 'Lev bulgare', 'Croatian kuna': 'Kuna croate',
    'Turkish lira': 'Livre turque', 'Russian ruble': 'Rouble russe',
    'Ukrainian hryvnia': 'Hryvnia ukrainienne', 'Saudi riyal': 'Riyal saoudien',
    'United Arab Emirates dirham': 'Dirham des Émirats',
    'Qatari riyal': 'Riyal qatari', 'Kuwaiti dinar': 'Dinar koweïtien',
    'Omani rial': 'Rial omanais', 'Bahraini dinar': 'Dinar bahreïni',
    'Jordanian dinar': 'Dinar jordanien', 'Lebanese pound': 'Livre libanaise',
    'Syrian pound': 'Livre syrienne', 'Iraqi dinar': 'Dinar irakien',
    'Iranian rial': 'Rial iranien', 'Afghan afghani': 'Afghani afghan',
    'Pakistani rupee': 'Roupie pakistanaise', 'Indian rupee': 'Roupie indienne',
    'Bangladeshi taka': 'Taka bangladais', 'Sri Lankan rupee': 'Roupie srilankaise',
    'Nepalese rupee': 'Roupie népalaise', 'Maldivian rufiyaa': 'Rufiyaa maldivien',
    'Thai baht': 'Baht thaïlandais', 'Vietnamese đồng': 'Dồng vietnamien',
    'Philippine peso': 'Peso philippin', 'Malaysian ringgit': 'Ringgit malaisien',
    'Singapore dollar': 'Dollar de Singapour', 'Indonesian rupiah': 'Roupie indonésienne',
    'Japanese yen': 'Yen japonais', 'South Korean won': 'Won sud-coréen',
    'Chinese yuan': 'Yuan chinois', 'Hong Kong dollar': 'Dollar de Hong Kong',
    'New Taiwan dollar': 'Dollar taïwanais', 'Australian dollar': 'Dollar australien',
    'New Zealand dollar': 'Dollar néo-zélandais', 'Canadian dollar': 'Dollar canadien',
    'Mexican peso': 'Peso mexicain', 'Brazilian real': 'Real brésilien',
    'Argentine peso': 'Peso argentin', 'Chilean peso': 'Peso chilien',
    'Colombian peso': 'Peso colombien', 'Peruvian sol': 'Sol péruvien',
    'Venezuelan bolívar': 'Bolivar vénézuélien', 'Uruguayan peso': 'Peso uruguayen',
    'Paraguayan guaraní': 'Guaraní paraguayen', 'Bolivian boliviano': 'Boliviano bolivien',
    'Egyptian pound': 'Livre égyptienne', 'South African rand': 'Rand sud-africain',
    'Nigerian naira': 'Naira nigérian', 'Ghanaian cedi': 'Cedi ghanéen',
    'West African CFA franc': 'Franc CFA (BCEAO)', 'Central African CFA franc': 'Franc CFA (BEAC)',
    'Congolese franc': 'Franc congolais', 'Ethiopian birr': 'Birr éthiopien',
    'Kenyan shilling': 'Shilling kényan', 'Tanzanian shilling': 'Shilling tanzanien',
    'Ugandan shilling': 'Shilling ougandais', 'Rwandan franc': 'Franc rwandais',
    'Burundian franc': 'Franc burundais', 'Malagasy ariary': 'Ariary malgache',
    'Mauritian rupee': 'Roupie mauricienne', 'Seychellois rupee': 'Roupie seychelloise',
    'Cape Verdean escudo': 'Escudo cap-verdien', 'Comorian franc': 'Franc comorien',
}

print("Traduction en français...")
updated = 0

for country in Country.objects.all():
    original_capital = country.capital
    original_currency = country.currency
    changed = False

    if country.capital in CAPITALS_FR:
        country.capital = CAPITALS_FR[country.capital]
        changed = True

    if country.currency in CURRENCIES_FR:
        country.currency = CURRENCIES_FR[country.currency]
        changed = True

    if changed:
        country.save()
        updated += 1
        print(f"✓ {country.code}: {country.name_fr}")

print(f"\nTerminé ! {updated} pays traduits.")