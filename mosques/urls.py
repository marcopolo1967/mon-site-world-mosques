from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import set_language

urlpatterns = [
    path('', views.home, name='home'),
    path('proposer/', views.proposer_mosquee, name='proposer'),
    path('admin/mosques/api/pending-count/', views.pending_propositions_count, name='pending_count'),
    path('carte/', views.carte_interactive, name='carte'),
    path('mosquee/<int:pk>/', views.details_mosquee, name='details_mosquee'),
    path('panorama/', views.panorama_wilayas, name='panorama'),
    path('api/countries/', views.countries_autocomplete, name='countries_autocomplete'),
    path('api/mosques/', views.mosques_autocomplete, name='mosques_autocomplete'),
    path('panorama/pays/<str:country_code>/', views.panorama_pays_detail, name='panorama_pays_detail'),
    path('i18n/setlang/', set_language, name='set_language'),
    path('get_wilayas/', views.get_wilayas, name='get_wilayas'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)