import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Mosquee_Annuaire.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

try:
    # On change le nom pour être SUR qu'il est nouveau
    username = 'rachid67'
    email = 'jack.meyers@yahoo.fr'
    password = 'Abde67zine*#'

    # On supprime l'ancien s'il existe pour repartir à zéro
    User.objects.filter(username=username).delete()

    # On crée le nouveau
    User.objects.create_superuser(username, email, password)
    print("✅ SUCCÈS : Superutilisateur 'superadmin' créé avec succès !")
except Exception as e:
    print(f"❌ ERREUR : {e}")