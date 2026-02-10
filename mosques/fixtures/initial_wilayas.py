# Script pour importer les 58 wilayas d'Algérie
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Mosquee_Annuaire.settings')
django.setup()

from mosques.models import Wilaya, Country

WILAYAS = [
    (1, "Adrar", "أدرار", "Adrar"),
    (2, "Chlef", "الشلف", "Chlef"),
    (3, "Laghouat", "الأغواط", "Laghouat"),
    (4, "Oum El Bouaghi", "أم البواقي", "Oum El Bouaghi"),
    (5, "Batna", "باتنة", "Batna"),
    (6, "Béjaïa", "بجاية", "Béjaïa"),
    (7, "Biskra", "بسكرة", "Biskra"),
    (8, "Béchar", "بشار", "Béchar"),
    (9, "Blida", "البليدة", "Blida"),
    (10, "Bouira", "البويرة", "Bouira"),
    (11, "Tamanrasset", "تمنراست", "Tamanrasset"),
    (12, "Tébessa", "تبسة", "Tébessa"),
    (13, "Tlemcen", "تلمسان", "Tlemcen"),
    (14, "Tiaret", "تيارت", "Tiaret"),
    (15, "Tizi Ouzou", "تيزي وزو", "Tizi Ouzou"),
    (16, "Alger", "الجزائر", "Algiers"),
    (17, "Djelfa", "الجلفة", "Djelfa"),
    (18, "Jijel", "جيجل", "Jijel"),
    (19, "Sétif", "سطيف", "Sétif"),
    (20, "Saïda", "سعيدة", "Saïda"),
    (21, "Skikda", "سكيكدة", "Skikda"),
    (22, "Sidi Bel Abbès", "سيدي بلعباس", "Sidi Bel Abbès"),
    (23, "Annaba", "عنابة", "Annaba"),
    (24, "Guelma", "قالمة", "Guelma"),
    (25, "Constantine", "قسنطينة", "Constantine"),
    (26, "Médéa", "المدية", "Médéa"),
    (27, "Mostaganem", "مستغانم", "Mostaganem"),
    (28, "M'Sila", "المسيلة", "M'Sila"),
    (29, "Mascara", "معسكر", "Mascara"),
    (30, "Ouargla", "ورقلة", "Ouargla"),
    (31, "Oran", "وهران", "Oran"),
    (32, "El Bayadh", "البيض", "El Bayadh"),
    (33, "Illizi", "إليزي", "Illizi"),
    (34, "Bordj Bou Arréridj", "برج بوعريريج", "Bordj Bou Arréridj"),
    (35, "Boumerdès", "بومرداس", "Boumerdès"),
    (36, "El Tarf", "الطارف", "El Tarf"),
    (37, "Tindouf", "تندوف", "Tindouf"),
    (38, "Tissemsilt", "تيسمسيلت", "Tissemsilt"),
    (39, "El Oued", "الوادي", "El Oued"),
    (40, "Khenchela", "خنشلة", "Khenchela"),
    (41, "Souk Ahras", "سوق أهراس", "Souk Ahras"),
    (42, "Tipaza", "تيبازة", "Tipaza"),
    (43, "Mila", "ميلة", "Mila"),
    (44, "Aïn Defla", "عين الدفلى", "Aïn Defla"),
    (45, "Naâma", "النعامة", "Naâma"),
    (46, "Aïn Témouchent", "عين تموشنت", "Aïn Témouchent"),
    (47, "Ghardaïa", "غرداية", "Ghardaïa"),
    (48, "Relizane", "غليزان", "Relizane"),
    (49, "Timimoun", "تيميمون", "Timimoun"),
    (50, "Bordj Badji Mokhtar", "برج باجي مختار", "Bordj Badji Mokhtar"),
    (51, "Ouled Djellal", "أولاد جلال", "Ouled Djellal"),
    (52, "Béni Abbès", "بني عباس", "Béni Abbès"),
    (53, "In Salah", "عين صالح", "In Salah"),
    (54, "In Guezzam", "عين قزام", "In Guezzam"),
    (55, "Touggourt", "تقرت", "Touggourt"),
    (56, "Djanet", "جانت", "Djanet"),
    (57, "El M'Ghair", "المغير", "El M'Ghair"),
    (58, "El Menia", "المنيعة", "El Menia"),
]


def create_wilayas():
    """Crée les 58 wilayas dans la base de données"""
    algeria = Country.objects.get(code='DZ')
    count = 0

    for code, name_fr, name_ar, name_en in WILAYAS:
        wilaya, created = Wilaya.objects.get_or_create(
            code=str(code).zfill(2),  # "1" → "01"
            country=algeria,
            defaults={
                'name_fr': name_fr,
                'name_ar': name_ar,
                'name_en': name_en
            }
        )
        if created:
            count += 1
            print(f"✅ Wilaya créée : {str(code).zfill(2)} - {name_fr}")

    print(f"\n📊 {count} wilayas ont été ajoutées à la base de données.")


if __name__ == "__main__":
    create_wilayas()