#!/usr/bin/env python
import sys, os, django, time
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory

# Sécurité pour la détection
DetectorFactory.seed = 0

# Configuration Django
sys.path.append('F:/Logiciels/Mosquee_Annuaire')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Mosquee_Annuaire.settings')
django.setup()

from mosques.models import Mosque


def get_clean_source(text_fr, text_ar, text_en):
    """Trouve le texte le plus riche et détecte sa vraie langue"""
    data = {'fr': text_fr, 'ar': text_ar, 'en': text_en}
    best_text = ""
    for lang, txt in data.items():
        if txt and len(txt.strip()) > len(best_text):
            best_text = txt.strip()

    if len(best_text) < 5: return None, None

    try:
        real_lang = detect(best_text)
        return real_lang, best_text
    except:
        return None, None


def process_field(instance, field_base_name):
    """Traite un groupe de champs (ex: 'description' ou 'history')"""
    # 1. Récupération des valeurs actuelles
    val_fr = getattr(instance, f"{field_base_name}_fr")
    val_ar = getattr(instance, f"{field_base_name}_ar")
    val_en = getattr(instance, f"{field_base_name}_en")

    # 2. Détection de la source réelle
    src_lang, src_text = get_clean_source(val_fr, val_ar, val_en)

    if not src_lang: return False

    updated = False
    targets = ['fr', 'ar', 'en']

    for lang in targets:
        field_name = f"{field_base_name}_{lang}"
        current_val = getattr(instance, field_name)

        # ON FORCE LA TRADUCTION SI :
        # - Le champ est vide
        # - OU si le champ contient la langue source alors qu'il devrait être traduit
        # (C'est ce qui corrige ton bug d'affichage inversé sur le site)
        should_translate = False
        if not current_val or len(current_val.strip()) < 5:
            should_translate = True
        elif lang != src_lang:
            try:
                # Si le texte actuel est dans la même langue que la source, on écrase
                if detect(current_val) == src_lang:
                    should_translate = True
            except:
                should_translate = True

        if should_translate and lang != src_lang:
            try:
                print(f"      -> Traduction {field_base_name} ({src_lang} > {lang})")
                translated = GoogleTranslator(source='auto', target=lang).translate(src_text)
                setattr(instance, field_name, translated)
                updated = True
                time.sleep(0.3)
            except Exception as e:
                print(f"      ❌ Erreur: {e}")

    return updated


def repair_all():
    print("🛠️ RÉPARATION PROFONDE : DESCRIPTION + HISTORIQUE")
    print("=" * 60)

    mosques = Mosque.objects.all()
    for m in mosques:
        print(f"📍 Mosquée: {m.name}")

        # On traite les deux séparément pour éviter les mélanges
        upd_desc = process_field(m, "description")
        upd_hist = process_field(m, "history")

        if upd_desc or upd_hist:
            m.save()
            print(f"   ✅ Mise à jour effectuée.")
        else:
            print(f"   ⏭️ Déjà parfaitement aligné.")


if __name__ == "__main__":
    repair_all()