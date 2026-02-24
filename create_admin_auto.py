import os
import django

# REMPLACEZ 'votre_projet' par le nom du dossier contenant settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'votre_projet.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

try:
    username = 'marcopolo67'
    email = 'jack.meyers@yahoo.fr'
    password = 'Abde67zine*#' # Changez-le !

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print("✅ SUCCÈS : Superutilisateur créé.")
    else:
        print("ℹ️ INFO : L'utilisateur existe déjà.")
except Exception as e:
    print(f"❌ ERREUR CRITIQUE : {e}")