from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count
from .models import Mosque, Country, Wilaya, Proposition, MosquePhoto
from .forms import PropositionForm
import cloudinary.uploader
import json
from django.utils.translation import get_language

import os
from django.core import management
from django.contrib.auth.decorators import user_passes_test
from io import StringIO

# ==================== VUES PRINCIPALES ====================

def home(request):
    """Vue pour la page d'accueil"""
    total_mosques = Mosque.objects.filter(is_verified=True).count()
    total_wilayas = Wilaya.objects.count()
    recent_mosques = Mosque.objects.filter(is_verified=True).order_by('-created_at')[:5]

    context = {
        'total_mosques': total_mosques,
        'total_wilayas': total_wilayas,
        'recent_mosques': recent_mosques,
    }
    return render(request, 'mosques/home.html', context)

def proposer_mosquee(request):
    """Vue pour le formulaire de proposition avec support multi-photos Cloudinary"""
    if request.method == 'POST':
        form = PropositionForm(request.POST, request.FILES)

        if form.is_valid():
            proposition = form.save(commit=False)

            # Gestion de l'IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
            proposition.contributor_ip = ip
            proposition.save()  # On sauvegarde d'abord la proposition pour avoir un ID
            print("--- DEBUG PHOTOS ---")
            print("FILES reçus :", request.FILES)
            # On change 'photo_files' par 'photos' pour correspondre au name="photos" du HTML
            files = request.FILES.getlist('photos')
            print("Liste extraite :", files)
            photo_count = 0

            if files:
                for f in files[:5]:  # Limite à 5 photos max
                    try:
                        # Avec CloudinaryField, on passe directement le fichier 'f'
                        # au champ 'image'. Django et Cloudinary gèrent l'upload.
                        from .models import PropositionPhoto
                        PropositionPhoto.objects.create(
                            proposition=proposition,
                            image=f
                        )
                        photo_count += 1
                    except Exception as e:
                        print(f"Erreur upload photo: {e}")
                        continue

            messages.success(
                request,
                f'✅ <strong>Merci pour votre proposition !</strong><br>'
                f'Votre proposition a été enregistrée avec {photo_count} photo(s) et sera examinée par notre équipe.'
            )
            return redirect('proposer')
    else:
        form = PropositionForm()

    stats = {
        'total_mosques': Mosque.objects.filter(is_verified=True).count(),
        'total_propositions': Proposition.objects.count(),
        'propositions_en_attente': Proposition.objects.filter(status='pending').count(),
    }

    return render(request, 'mosques/proposer.html', {'form': form, 'stats': stats})


def carte_interactive(request):
    """Vue pour la carte interactive des mosquées (Monde)"""
    mosques = Mosque.objects.filter(
        is_verified=True,
        latitude__isnull=False,
        longitude__isnull=False
    )

    mosques_data = []
    pays_codes = set()

    # Correspondance nom → code ISO
    correspondances = {
        "Algérie": "DZ", "Algeria": "DZ", "DZ": "DZ",
        "France": "FR", "França": "FR",
        "Maroc": "MA", "Morocco": "MA",
        "Tunisie": "TN", "Tunisia": "TN",
        "Égypte": "EG", "Egypt": "EG",
        "Arabie saoudite": "SA", "Saudi Arabia": "SA",
        "Turquie": "TR", "Turkey": "TR",
        "États-Unis": "US", "United States": "US", "USA": "US",
        "Royaume-Uni": "GB", "United Kingdom": "GB", "UK": "GB",
        "Espagne": "ES", "Spain": "ES",
        "Allemagne": "DE", "Germany": "DE",
        "Italie": "IT", "Italy": "IT",
        "Pakistan": "PK", "باكستان": "PK", "پاکستان": "PK",
    }

    # ========== FONCTION DE NORMALISATION (EN DEHORS de la boucle) ==========
    import unicodedata

    def remove_accents(text):
        """Enlève les accents d'un texte"""
        text = unicodedata.normalize('NFD', str(text))
        text = text.encode('ascii', 'ignore').decode('utf-8')
        return text

    # ========================================================================

    for mosque in mosques:
        country_name = str(mosque.country)

        # ========== RECHERCHE INSENSIBLE AUX ACCENTS ==========
        # RECHERCHE EN 2 ÉTAPES :
        country_code = None

        # 1. D'abord chercher dans arabic_to_french (pour l'arabe)
        arabic_to_french = {
            'الجزائر': 'DZ',
            'الـجزائر': 'DZ',
            'مصر': 'EG',
            'المغرب': 'MA',
            'تونس': 'TN',
            'السعودية': 'SA',
            'تركيا': 'TR',
            'فرنسا': 'FR'
        }

        if country_name in arabic_to_french:
            country_code = arabic_to_french[country_name]

            print(f"✅ Trouvé '{country_name}' dans arabic_to_french: {country_code}")


        else:
            print(f"❌ '{country_name}' NON trouvé dans arabic_to_french")
            print(f"   Clés disponibles: {list(arabic_to_french.keys())}")

            # 2. Si pas en arabe, chercher dans correspondances (insensible aux accents)
            normalized_input = remove_accents(country_name).lower()

            for key, value in correspondances.items():
                if remove_accents(key).lower() == normalized_input:
                    country_code = value
                    break

            # 3. Si toujours pas trouvé, prendre les 2 premiers caractères
            if not country_code:
                # Deviner par le nom
                country_lower = country_name.lower()
                if 'alg' in country_lower or 'جزائر' in country_name:
                    country_code = 'DZ'
                elif 'maroc' in country_lower or 'مغرب' in country_name:
                    country_code = 'MA'
                elif 'tunis' in country_lower or 'تونس' in country_name:
                    country_code = 'TN'
                elif 'franc' in country_lower or 'فرنسا' in country_name:
                    country_code = 'FR'
                else:
                    country_code = country_name[:2].upper()

        pays_codes.add(country_code)

        mosques_data.append({
            'id': mosque.id,
            'name': mosque.name,
            'latitude': float(mosque.latitude),
            'longitude': float(mosque.longitude),
            'city': mosque.city,
            'address': mosque.address or "",
            'wilaya': mosque.wilaya.name_fr if mosque.wilaya else '',
            'country': country_name,
            'country_code': country_code,
            'description': mosque.description or '',
            'history': mosque.history or '',
            'wilaya_id': mosque.wilaya.code if mosque.wilaya else 0,
        })

    wilayas = Wilaya.objects.all().order_by('name_fr')

    # Récupérer les noms des pays depuis la base Country
    pays_avec_noms = []
    for code in sorted(pays_codes):
        try:
            country = Country.objects.get(code=code)
            pays_avec_noms.append({
                'code': code,
                'name_fr': country.name_fr,
                'name_ar': country.name_ar or country.name_fr,
                'name_en': country.name_en or country.name_fr,
            })
        except Country.DoesNotExist:
            # Fallback
            pays_avec_noms.append({
                'code': code,
                'name_fr': code,
                'name_ar': code,
                'name_en': code,
            })

    print("=== DEBUG CARTE ===")
    print("pays_codes:", pays_codes)
    print("pays_avec_noms:", pays_avec_noms)
    print("pays_avec_noms length:", len(pays_avec_noms))

    # Récupération de tous les pays pour l'autocomplétion JS
    all_countries_qs = Country.objects.all().order_by('name_fr')
    all_countries_list = []
    for c in all_countries_qs:
        all_countries_list.append({
            'code': c.code,
            'name_fr': c.name_fr,
            'name_ar': c.name_ar or c.name_fr,
            'name_en': c.name_en or c.name_fr,
            'flag': c.flag or '🏳️',
        })

    context = {
        'LANGUAGE_CODE': get_language(),
        'mosques_data': mosques_data,
        'wilayas': wilayas,
        'pays_presents': sorted(list(pays_codes)),
        'pays_avec_noms': pays_avec_noms,
        'total_mosques': len(mosques_data),
        'countries_json': json.dumps(all_countries_list, ensure_ascii=False)  # Liste réelle envoyée au JS
    }
    return render(request, 'mosques/carte.html', context)


def details_mosquee(request, pk):
    # On utilise select_related pour charger la wilaya en même temps et éviter les erreurs de traduction
    mosque = get_object_or_404(Mosque.objects.select_related('wilaya'), pk=pk)

    # On récupère toutes les photos approuvées pour la galerie
    photos = mosque.photos.filter(is_approved=True).order_status = 'approved'  # Optionnel si déjà géré par l'objet

    context = {
        'mosque': mosque,
        'photos': mosque.photos.filter(is_approved=True),
        'LANGUAGE_CODE': get_language(),  # On s'assure que le template reçoit la langue active
    }
    return render(request, 'mosques/details_mosquee.html', context)


def panorama_wilayas(request):
    """Vue pour le panorama mondial"""
    countries_data = []
    all_countries = Country.objects.all().order_by('name_fr')

    for c in all_countries:
        # On compte toutes les mosquées liées à ce pays
        count = Mosque.objects.filter(country_link=c, is_verified=True).count()

        countries_data.append({
            'name': c.name_fr,
            'name_fr': c.name_fr,
            'name_ar': c.name_ar or '',
            'name_en': c.name_en or '',
            'code': c.code or '',
            'flag': c.flag or '🏳️',
            'continent': c.continent.lower() if c.continent else 'af',
            'mosque_count': count,  # Assure-toi que c'est le même nom partout
        })

    # On récupère le chiffre spécifique pour l'Algérie
    # On utilise name_fr='Algérie' pour être 100% sûr
    algeria_obj = Mosque.objects.filter(country_link__name_fr='Algérie', is_verified=True)

    context = {
        'countries_json': json.dumps(countries_data, ensure_ascii=False),
        'wilayas': Wilaya.objects.annotate(
            mosque_count=Count('mosque', filter=Q(mosque__is_verified=True))
        ).order_by('code'),
        'algeria_count': algeria_obj.count(),  # Cette variable va au gros badge en haut
    }
    return render(request, 'mosques/wilayas.html', context)


def panorama_pays_detail(request, country_code):
    """Vue pour afficher les détails d'un pays (villes + statistiques)"""

    try:
        country = Country.objects.filter(code__iexact=country_code).first()
        if not country:
            country = Country.objects.filter(name_fr__iexact=country_code).first()

        mosques_count = Mosque.objects.filter(
            country_link=country,
            is_verified=True
        ).count()

        mosques = Mosque.objects.filter(
            country_link=country,
            is_verified=True
        ).select_related('wilaya')

        villes_stats = []
        for mosque in mosques:
            ville_name = mosque.city or "Non spécifié"
            existing = next((v for v in villes_stats if v['name'] == ville_name), None)
            if existing:
                existing['count'] += 1
            else:
                villes_stats.append({
                    'name': ville_name,
                    'count': 1,
                    'wilaya': mosque.wilaya.name_fr if mosque.wilaya else ''
                })

        villes_stats.sort(key=lambda x: x['count'], reverse=True)

        context = {
            'country': country,
            'country_code': country_code,
            'mosques_count': mosques_count,
            'villes_stats': villes_stats,
            'total_villes': len(villes_stats),
            'LANGUAGE_CODE': request.LANGUAGE_CODE,
        }

        if country and (country.name_fr == "Algérie" or country_code in ["ALG", "DZ"]):
            context['wilayas'] = Wilaya.objects.annotate(
                mosque_count=Count('mosque', filter=Q(mosque__is_verified=True))
            ).order_by('code')

        return render(request, 'mosques/pays_detail.html', context)

    except Exception:
        messages.error(request, "Erreur lors du chargement des données")
        return redirect('panorama')


# ==================== APIS ====================

def countries_autocomplete(request):
    q = request.GET.get('q', '').strip()
    continent = request.GET.get('continent', '').strip()

    countries = Country.objects.all()

    if continent:
        countries = countries.filter(continent__iexact=continent)

    if q:
        countries = countries.filter(
            Q(name_fr__icontains=q) |
            Q(name_en__icontains=q) |
            Q(name_ar__icontains=q)
        )

    results = []
    for c in countries.order_by('name_fr')[:20]:
        mosque_count = Mosque.objects.filter(
            Q(country=c.name_fr) | Q(country=c.code),
            is_verified=True
        ).count()

        results.append({
            'code': c.code or '',
            'name_fr': c.name_fr or '',
            'name_en': c.name_en or '',
            'name_ar': c.name_ar or '',
            'flag': c.flag or '🏳️',
            'mosque_count': mosque_count,
        })

    return JsonResponse(results, safe=False)

def mosques_autocomplete(request):
    """API pour retourner les mosquées filtrées par country_id ou wilaya_id"""
    country_id = request.GET.get('country_id')
    wilaya_id = request.GET.get('wilaya_id')

    mosques_qs = Mosque.objects.filter(is_verified=True)

    if wilaya_id:
        mosques_qs = mosques_qs.filter(wilaya_id=wilaya_id)
    elif country_id:
        try:
            country = Country.objects.get(id=country_id)
            mosques_qs = mosques_qs.filter(country=country.name)
        except Country.DoesNotExist:
            return JsonResponse([], safe=False)

    mosques_data = []
    for m in mosques_qs:
        mosques_data.append({
            'id': m.id,
            'name': m.name,
            'address': m.address,
            'city': m.city,
            'wilaya': m.wilaya.name_fr if m.wilaya else '',
            'country': m.country,
            'latitude': float(m.latitude) if m.latitude else None,
            'longitude': float(m.longitude) if m.longitude else None,
        })

    return JsonResponse(mosques_data, safe=False)

def pending_propositions_count(request):
    """API pour le compteur de notifications admin"""
    if request.user.is_staff:
        count = Proposition.objects.filter(status='pending').count()
        return JsonResponse({'count': count})
    return JsonResponse({'count': 0})

def get_wilayas(request):
    """API pour retourner toutes les wilayas avec support multilingue"""
    wilayas = Wilaya.objects.all().order_by('code')
    data = []
    for w in wilayas:
        data.append({
            'id': w.id,
            'code': w.code,
            'name_fr': w.name_fr,
            'name_ar': w.name_ar or w.name_fr,
            'name_en': w.name_en or w.name_fr,
        })
    return JsonResponse(data, safe=False)


def get_pending_propositions_count(request):
    pending_qs = Proposition.objects.filter(status='pending').order_by('-created_at')
    count = pending_qs.count()
    # On récupère les noms des 5 dernières pour le "survol"
    names = list(pending_qs.values_list('name', flat=True)[:5])

    return JsonResponse({
        'count': count,
        'names': names
    })


# --- AVANT : Fin de ton fichier views.py ---

# --- APRÈS : Ajoute ce bloc ---
import os
from django.core import management
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from io import StringIO


@user_passes_test(lambda u: u.is_superuser)
def export_data_secure(request):
    """Génère un export JSON des mosquées pour synchronisation locale"""
    output = StringIO()
    # On exporte l'app 'mosques' pour récupérer propositions et mosquées
    management.call_command('dumpdata', 'mosques', indent=2, stdout=output)

    response = HttpResponse(output.getvalue(), content_type="application/json")
    response['Content-Disposition'] = 'attachment; filename="backup_mosquees.json"'
    return response