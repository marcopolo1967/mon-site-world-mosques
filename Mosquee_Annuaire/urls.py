from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from mosques import views

# ================================================================
# 1. URLS GLOBALES (Sans préfixe de langue)
# ================================================================
# On place ici uniquement ce qui ne doit JAMAIS avoir de /fr/ ou /ar/
urlpatterns = [
    # Le "bureau de change" : indispensable pour changer de langue via le menu
    path('i18n/', include('django.conf.urls.i18n')),
]

# ================================================================
# 2. URLS TRADUITES (Avec préfixe /fr/, /ar/, etc.)
# ================================================================
# On regroupe tout ici pour que Django gère automatiquement la langue
urlpatterns += i18n_patterns(

    # 🍯 Le piège : si quelqu'un tape /admin/, il tombe ici
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),

    # L'administration SECRÈTE : placée ici pour éviter les conflits de redirection
    # Elle sera accessible via /fr/secure-admin-5921/
    path('secure-admin-5921/', admin.site.urls),

    # Toutes les pages de ton application (Accueil, Carte, Proposer, etc.)
    path('', include('mosques.urls')),

    # API pour le badge des propositions en attente dans l'admin
    path('admin/mosques/api/pending-count/', views.get_pending_propositions_count, name='pending_count'),

    # Force l'affichage du préfixe même pour la langue par défaut (ex: /fr/)
    prefix_default_language=True,
)

# ================================================================
# 3. GESTION DES FICHIERS STATIQUES ET MÉDIAS
# ================================================================
# Uniquement actif en mode développement (DEBUG = True)
if settings.DEBUG:
    # Pour afficher les photos des mosquées (Media)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Pour charger le CSS et le JavaScript (Static)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ================================================================
# 4. PERSONNALISATION DE L'INTERFACE D'ADMINISTRATION
# ================================================================
admin.site.site_header = "Administration des Mosquées"      # Titre dans la barre bleue
admin.site.site_title = "Gestion Annuaire"                   # Titre dans l'onglet du navigateur
admin.site.index_title = "Bienvenue sur votre espace de gestion" # Message d'accueil sur le tableau de bord