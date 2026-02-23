# fix_sites.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Mosquee_Annuaire.settings')
django.setup()

from django.contrib.sites.models import Site
from django.db import connection, transaction

print("=== RÉPARATION DU SITE DJANGO ===")

# 1. Videz le cache
from django.core.cache import cache
cache.clear()
print("✅ Cache vidé")

# 2. Supprimez TOUS les sites
Site.objects.all().delete()
print("✅ Anciens sites supprimés")

# 3. Créez le site avec ID=1 (IMPORTANT)
with transaction.atomic():
    site = Site.objects.create(
        id=1,  # FORCEZ ID=1
        domain='localhost:8000',
        name='Mosquee Annuaire'
    )
    print(f"✅ Site créé: ID={site.id}, Domain={site.domain}")

# 4. Vérifiez
sites = Site.objects.all()
print(f"\n✅ {sites.count()} site(s) dans la base:")
for s in sites:
    print(f"   - ID {s.id}: {s.domain}")

print("\n=== RÉPARATION TERMINÉE ===")
print("Redémarrez maintenant: python manage.py runserver")