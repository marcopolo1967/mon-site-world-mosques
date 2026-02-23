from django.contrib import admin, messages
from modeltranslation.admin import TranslationAdmin
from .models import Wilaya, Mosque, MosquePhoto, Proposition, MosqueWithPhotos, Country, Proposition, PropositionPhoto
from .forms import MosqueAdminForm
from django.utils import timezone
from django import forms
from datetime import timedelta
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.utils.safestring import mark_safe
from googletrans import Translator
from django.forms.widgets import ClearableFileInput
from django.forms import FileInput
from mosques.utils.translation import translate_text_to_3_langs


class MosquePhotoInline(admin.TabularInline):
    model = MosquePhoto
    extra = 3  # Affiche 3 emplacements vides par défaut
    fields = ('image', 'caption', 'is_approved', 'uploaded_by')
    readonly_fields = ('uploaded_by',)

    # Cette option permet de voir la miniature dans l'inline
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: auto; border-radius: 4px;"/>', obj.image.url)
        return "Pas d'image"

    readonly_fields = ('image_preview',)
    fields = ('image', 'image_preview', 'caption', 'is_approved')

    def has_delete_permission(self, request, obj=None):
        return True


# ================================================
# ADMIN PRINCIPAL DE LA MOSQUÉE
# ================================================
@admin.register(Mosque)
class MosqueAdmin(TranslationAdmin):


    list_display = ('name', 'country_link', 'display_wilaya', 'city', 'photo_count_display', 'view_photos_link')
    list_filter = ('country_link', 'wilaya', 'is_verified')
    search_fields = ('name', 'city', 'village', 'address')
    list_per_page = 50
    readonly_fields = ('created_at', 'updated_at', 'current_photos_preview', 'upload_photos_field')

    # ================================================
    # MEDIA : scripts et CSS personnalisés
    # ================================================
    class Media:
        js = (
            'admin/js/toggle_wilaya.js',
            'admin/js/photo_preview.js',
            'admin/js/fix_form_enctype.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'all': (
                'admin/css/photo_preview.css',
                'modeltranslation/css/tabbed_translation_fields.css',
            )
        }

    # ================================================
    # MÉTHODES D'AFFICHAGE DANS LA LISTE
    # ================================================
    def display_country(self, obj):
        return obj.country if obj.country else "—"
    display_country.short_description = "Pays"
    display_country.admin_order_field = 'country'

    def display_wilaya(self, obj):
        """Affiche la wilaya uniquement pour l'Algérie"""
        if obj.country and obj.wilaya:
            import unicodedata

            def remove_accents(text):
                text = unicodedata.normalize('NFD', text)
                text = text.encode('ascii', 'ignore').decode('utf-8')
                return text.lower()

            normalized_country = remove_accents(str(obj.country).lower())
            french_variations = ['algerie', 'algeria', 'dz']
            arabic_variations = ['الجزائر', 'الـجزائر', 'جزائر']
            if any(v in normalized_country for v in french_variations) or any(v in obj.country for v in arabic_variations):
                return f"{obj.wilaya.code} - {obj.wilaya.name_fr}"
        return "—"
    display_wilaya.short_description = "Wilaya (Algérie)"
    display_wilaya.admin_order_field = 'wilaya'

    def photo_count_display(self, obj):
        count = obj.photos.count()
        if count == 0:
            return format_html('<span style="color:gray;">📷 Aucune</span>')
        return format_html('<span style="color:green; font-weight:bold;">📸 {} photo{}</span>', count, 's' if count > 1 else '')
    photo_count_display.short_description = "Photos"

    def view_photos_link(self, obj):
        if obj.photos.count() == 0:
            return "—"
        url = reverse('admin:mosque_photos_detail', args=[obj.id])
        return format_html(
            '<a href="{}" class="button" style="padding: 5px 10px; background: #417690; color: white; text-decoration: none; border-radius: 3px; font-size: 12px;">👁️ Voir {} photo{}</a>',
            url, obj.photos.count(), 's' if obj.photos.count() > 1 else ''
        )
    view_photos_link.short_description = "Voir photos"

    # ================================================
    # FIELDSETS POUR LA PAGE D'ÉDITION
    # ================================================

    group_fieldsets = True  # Regroupe les champs traduits si besoin

    fieldsets = (
        ('Informations principales', {
            'fields': (
                'name_fr', 'name_ar', 'name_en',  # On remplace 'name' par les 3 langues
                'country_link', 'wilaya', 'city', 'village', 'address'
            )
        }),

        ('Coordonnées GPS', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),

        ('Gestion des Photos', {
            # La virgule après 'upload_photos_field' est cruciale si c'était le seul élément,
            # mais ici on met les deux :
            'fields': ('current_photos_preview', 'upload_photos_field'),
            'description': 'L\'aperçu montre les photos actuelles. Utilisez le champ ci-dessous pour en ajouter plusieurs d\'un coup.'
        }),

        ('Description et Histoire', {
            'fields': ('description_fr', 'history_fr'),
        }),

        ('Modération', {
            'fields': ('is_verified',),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        files = request.FILES.getlist('bulk_photos')

        if files:
            from .models import MosquePhoto
            photo_count = 0
            for f in files:
                # 2. On ajoute 'is_approved=True' (ou le nom exact de votre champ de validation)
                # Vérifiez dans votre modèle MosquePhoto si le champ s'appelle 'is_approved' ou 'is_verified'
                MosquePhoto.objects.create(
                    mosque=obj,
                    image=f,
                    is_approved=True
                )
                photo_count += 1

            self.message_user(request, f"✅ {photo_count} photos ajoutées et approuvées automatiquement.")

    # LA MÉTHODE DOIT ÊTRE À L'INTÉRIEUR DE LA CLASSE
    def upload_photos_field(self, obj):
        return format_html(
            '<input type="file" name="bulk_photos" multiple accept="image/*" class="form-control" style="max-width: 300px;">'
        )

    upload_photos_field.short_description = "➕ Ajouter des photos"


    # ================================================
    # APERÇU DES PHOTOS EXISTANTES DANS LA PAGE D'EDIT
    # ================================================
    def current_photos_preview(self, obj):
        if obj.id:
            photos = obj.photos.all()[:6]
            if photos.exists():
                html = '<div style="margin: 20px 0; padding: 15px; background: #f8f8f8; border-radius: 8px;">'
                html += '<h3 style="margin-top: 0;">📷 Photos existantes</h3>'
                html += '<div style="display: flex; flex-wrap: wrap; gap: 10px; margin: 15px 0;">'

                for photo in photos:
                    html += f'''
                    <div style="text-align: center; width: 100px;">
                        <a href="{photo.image.url}" target="_blank" style="text-decoration: none;">
                            <img src="{photo.image.url}" 
                                 style="width: 80px; height: 80px; object-fit: cover; border-radius: 5px; border: 2px solid #ddd;">
                        </a>
                        <div style="font-size: 10px; margin-top: 5px; color: #666;">
                            {photo.created_at.strftime('%d/%m/%y')}<br>
                            📝 {photo.caption or "—"}
                        </div>
                    </div>
                    '''

                total_photos = obj.photos.count()
                if total_photos > 6:
                    html += f'<div style="align-self: center; color: #666; font-size: 12px;">+ {total_photos - 6} autres photos</div>'
                detail_url = reverse('admin:mosque_photos_detail', args=[obj.id])
                html += '</div>'
                html += f'<a href="{detail_url}" style="display: inline-block; margin-top: 10px; padding: 8px 15px; background: #5a9bd5; color: white; text-decoration: none; border-radius: 4px;">📂 Gérer toutes les photos ({total_photos})</a>'
                html += '</div>'
                return format_html(html)
        return format_html('<p style="color: #999; font-style: italic;">Aucune photo pour le moment</p>')
    current_photos_preview.short_description = "Photos existantes"

    # ================================================
    # URLS PERSONNALISÉES POUR LA GESTION DES PHOTOS
    # ================================================
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:mosque_id>/photos/',
                 self.admin_site.admin_view(self.mosque_photos_view),
                 name='mosque_photos_detail'),
            path('<int:mosque_id>/photos/<int:photo_id>/delete/',
                 self.admin_site.admin_view(self.delete_photo_view),
                 name='delete_mosque_photo'),
            path('<int:mosque_id>/photos/<int:photo_id>/toggle-approve/',
                 self.admin_site.admin_view(self.toggle_approve_photo_view),
                 name='toggle_approve_mosque_photo'),
        ]
        return custom_urls + urls

    # ================================================
    # VUES PERSONNALISÉES
    # ================================================
    def mosque_photos_view(self, request, mosque_id):
        mosque = get_object_or_404(Mosque, id=mosque_id)
        photos = mosque.photos.all().order_by('-created_at')

        if request.method == 'POST':
            # 1️⃣ Mettre à jour les captions existantes
            for key, value in request.POST.items():
                if key.startswith('caption_'):
                    try:
                        photo_id = int(key.split('_')[1])
                        photo = MosquePhoto.objects.get(id=photo_id, mosque=mosque)
                        photo.caption = value.strip()
                        photo.save()
                    except (ValueError, MosquePhoto.DoesNotExist):
                        pass  # Ignore les erreurs si id invalide ou photo inexistante

            # 2️⃣ Ajouter de nouvelles photos
            new_photos = request.FILES.getlist('new_photos')
            if new_photos:
                try:
                    for photo_file in new_photos:
                        MosquePhoto.objects.create(
                            mosque=mosque,
                            image=photo_file,
                            uploaded_by=request.user.username,
                            is_approved=True
                        )
                    messages.success(request, f"{len(new_photos)} photo(s) ajoutée(s) avec succès!")
                except Exception as e:
                    messages.error(request, f"❌ Erreur lors du téléchargement : {str(e)}")

            return redirect('admin:mosque_photos_detail', mosque_id=mosque_id)

        # --------------------------
        # CONTEXT POUR LE TEMPLATE
        # --------------------------
        context = {
            'mosque': mosque,
            'photos': photos,
            'title': f'Gestion des photos - {mosque.name}',
            'opts': self.model._meta,
            'app_label': self.model._meta.app_label,
        }
        return render(request, 'mosques/mosque_photos_manage.html', context)

    def delete_photo_view(self, request, mosque_id, photo_id):
        if request.method == 'POST':
            photo = get_object_or_404(MosquePhoto, id=photo_id, mosque_id=mosque_id)
            photo_name = str(photo.image)
            photo.delete()
            messages.success(request, f"Photo '{photo_name}' supprimée avec succès!")
        return redirect('admin:mosque_photos_detail', mosque_id=mosque_id)

    def toggle_approve_photo_view(self, request, mosque_id, photo_id):
        if request.method == 'POST':
            photo = get_object_or_404(MosquePhoto, id=photo_id, mosque_id=mosque_id)
            photo.is_approved = not photo.is_approved
            photo.save()
            status = "approuvée" if photo.is_approved else "désapprouvée"
            messages.success(request, f"Photo {status} avec succès!")
        return redirect('admin:mosque_photos_detail', mosque_id=mosque_id)


class PropositionPhotoInline(admin.TabularInline):
    model = PropositionPhoto
    extra = 1
    fields = ('image', 'created_at')
    readonly_fields = ('created_at',)
    show_change_link = True

    def has_delete_permission(self, request, obj=None):
        return True

# ====================================================================
# ADMIN SPÉCIAL POUR VOIR TOUTES LES MOSQUÉES AVEC PHOTOS
# ====================================================================

@admin.register(MosqueWithPhotos)
class MosquePhotosViewAdmin(admin.ModelAdmin):
    """
    Vue spéciale : Liste TOUTES les mosquées avec photos
    """

    list_display = ('name', 'city', 'display_country', 'photo_count_display', 'view_photos_link')
    list_filter = ('country', 'wilaya', 'is_verified')  # Inversion pays/wilaya dans le filtre
    search_fields = ('name', 'city', 'village', 'address', 'country__name_fr', 'wilaya__name_fr')
    list_per_page = 50

    def display_country(self, obj):
        """Affiche le pays (texte seulement)"""
        return obj.country if obj.country else "—"

    display_country.short_description = "Pays"
    display_country.admin_order_field = 'country'

    # Désactiver modification
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # Filtrer uniquement mosquées avec photos
    def get_queryset(self, request):
        return Mosque.objects.filter(photos__isnull=False).distinct()

    def photo_count_display(self, obj):
        count = obj.photos.count()

        print(f"=== DEBUG MosqueAdmin ===")
        print(f"Mosquée: {obj.name} (ID: {obj.id})")
        print(f"obj.photos.count() = {count}")
        print(f"Type de obj.photos: {type(obj.photos)}")
        print(f"Relation existe? {hasattr(obj, 'photos')}")
        return format_html('<span style="color:green; font-weight:bold;">📸 {}</span>', count)

    photo_count_display.short_description = "Photos"

    def view_photos_link(self, obj):
        url = reverse('admin:mosque_photos_detail', args=[obj.id])
        return format_html(
            '<a href="{}" class="button" style="padding: 5px 10px; background: #417690; color: white; text-decoration: none; border-radius: 3px;">👁️ Voir photos</a>',
            url
        )

    view_photos_link.short_description = "Action"


# ====================================================================
# ADMIN DES WILAYAS
# ====================================================================

@admin.register(Wilaya)
class WilayaAdmin(admin.ModelAdmin):
    list_display = ('code', 'name_fr', 'name_ar')
    search_fields = ('name_fr', 'name_ar')




class PropositionAdminForm(forms.ModelForm):
    photos = forms.FileField(
        required=False,
        label="📸 Ajouter des photos"
    )

    class Meta:
        model = Proposition
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=commit)

        # 1. Gestion des photos (CORRECTION : enumerate donne (index, file))
        files = self.files.getlist('photos') if 'photos' in self.files else []
        if files:
            for index, file in enumerate(files):  # CORRECTION ICI
                MosquePhoto.objects.create(
                    mosque=instance,
                    image=file,  # file est l'objet fichier, pas le tuple
                    uploaded_by="Admin",
                    is_approved=True,
                )

        # 2. TRADUCTION AUTOMATIQUE (CORRECTION : utiliser description/history, pas *_fr)
        try:
            from googletrans import Translator
            translator = Translator()

            # CORRECTION : Utiliser les champs ORIGINAUX (français)
            french_description = instance.description  # Champ original = français
            french_history = instance.history  # Champ original = français

            # Traduction Description
            if french_description and (not instance.description_ar or not instance.description_en):
                if not instance.description_ar:
                    try:
                        translated_ar = translator.translate(french_description, dest='ar')
                        instance.description_ar = translated_ar.text
                    except:
                        instance.description_ar = french_description  # Fallback français

                if not instance.description_en:
                    try:
                        translated_en = translator.translate(french_description, dest='en')
                        instance.description_en = translated_en.text
                    except:
                        instance.description_en = french_description  # Fallback français

            # Traduction Historique
            if french_history and (not instance.history_ar or not instance.history_en):
                if not instance.history_ar:
                    try:
                        translated_ar = translator.translate(french_history, dest='ar')
                        instance.history_ar = translated_ar.text
                    except:
                        instance.history_ar = french_history  # Fallback français

                if not instance.history_en:
                    try:
                        translated_en = translator.translate(french_history, dest='en')
                        instance.history_en = translated_en.text
                    except:
                        instance.history_en = french_history  # Fallback français

            if instance.description_ar or instance.description_en or instance.history_ar or instance.history_en:
                instance.save()  # Sauvegarder seulement si changements

        except Exception as e:
            print(f"⚠️ Traduction échouée: {e}")
            # Continuer sans traduction

        return instance


# ====================================================================
# ADMIN DES PROPOSITIONS (GARDE TON CODE EXISTANT)
# ====================================================================

@admin.register(Proposition)
class PropositionAdmin(admin.ModelAdmin):


    readonly_fields = ('created_at', 'photos_display')

    # 1. Configuration de la liste
    list_display = ('name', 'country', 'wilaya', 'city', 'created_at', 'status_colored', 'apercu_photo')
    list_filter = ('wilaya', 'country', 'status')
    search_fields = ('name', 'city', 'email', 'phone')
    list_per_page = 50

    def get_urls(self):
        """Ajoute l'URL API pour le badge"""
        urls = super().get_urls()
        custom_urls = [
            path('api/pending-count/',
                 self.admin_site.admin_view(self.pending_count_api),
                 name='pending_count_api'),
        ]
        return custom_urls + urls

    def pending_count_api(self, request):
        """API qui compte les propositions en attente"""
        from django.http import JsonResponse
        count = Proposition.objects.filter(status='pending').count()
        return JsonResponse({'count': count})

    def get_queryset(self, request):
        """
        N'affiche que les propositions EN ATTENTE ou REJETÉES
        Les propositions approuvées sont masquées de la liste principale
        """
        # Appelle le queryset parent (toutes les propositions)
        qs = super().get_queryset(request)
        # Filtre pour exclure les propositions avec status='approved'
        return qs.exclude(status='approved')

    def status_colored(self, obj):
        if obj.status == 'approved':
            return format_html(
                '<span style="color: green; font-weight: bold;">'
                '✅ APPROUVÉE (créée en mosquée)'
                '</span>'
            )
        elif obj.status == 'pending':
            return format_html(
                '<span style="color: orange; font-weight: bold;">'
                '⏳ En attente'
                '</span>'
            )
        elif obj.status == 'rejected':
            return format_html(
                '<span style="color: red; font-weight: bold;">'
                '❌ Rejetée'
                '</span>'
            )
        return obj.get_status_display()

    status_colored.short_description = "Statut"
    status_colored.admin_order_field = 'status'


    # 2. Ordre CORRECT des champs dans le formulaire
    fieldsets = (
        ('Informations principales', {
            'fields': (
                'name',  # 1. Nom
                'country',  # 2. Pays
                'wilaya',  # 3. Wilaya
                'city',  # 4. Ville
                'village',  # 5. Village
                'address',  # 6. Adresse
            )
        }),
        ('Descriptions', {
            'fields': (
                'description',
                'history',
            )
        }),
        ('Coordonnées GPS', {
            'fields': (
                'latitude',
                'longitude',
            ),
            'classes': ('collapse',)
        }),
        ('Contact', {
            'fields': (
                'contributor_email',
            )
        }),
        ('Photos reçues', {
            'fields': ('photos_display',),
        }),
        ('Statut', {
            'fields': (
                'status',
                'review_notes',
            )
        }),
        ('Actions', {
            'fields': (),
            'description': format_html('''
                    <div style="background: #e8f5e8; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                        <button type="submit" name="_approve" value="1" 
                                style="background: #4CAF50; color: white; padding: 10px 20px; 
                                       border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">
                            ✅ Approuver et créer la mosquée
                        </button>
                        <p style="margin-top: 10px; font-size: 12px; color: #666;">
                            Cette action créera une mosquée dans la liste principale et transférera les photos.
                        </p>
                    </div>
                ''')
        }),
    )

    class Media:
        js = (
            'admin/js/toggle_wilaya.js',
            'admin/js/photo_preview.js',  # Même script que MosqueAdmin
            'admin/js/proposition_notifications.js',
        )
        css = {
            'all': ('admin/css/photo_preview.css',)
        }

    def photo_count(self, obj):
        # Puisque c'est maintenant un CloudinaryField, s'il existe, il y a 1 photo
        return "📸 1" if obj.photos else "❌"

    def apercu_photo(self, obj):
        first_photo = obj.proposition_photos.first()
        if first_photo:
            return format_html('<img src="{}" style="width:50px;height:50px;object-fit:cover;border-radius:4px;">', first_photo.image.url)
        return "❌"

    def photos_display(self, obj):
        count = obj.proposition_photos.count()
        if count == 0:
            return format_html('<b style="color:red;">Zéro photo trouvée en base de données pour l\'ID {}</b>', obj.id)

        html = f'<b>Nombre de photos : {count}</b><br><div style="display:flex; gap:10px;">'
        for p in obj.proposition_photos.all():
            if p.image:
                html += f'<img src="{p.image.url}" style="width:100px; height:100px; object-fit:cover;">'
        html += '</div>'
        return format_html(html)


    def response_change(self, request, obj):
        """Quand l'admin clique sur 'Approuver' - Version AVEC traduction et multi-photos Cloudinary"""

        if '_approve' in request.POST:
            from .models import Mosque, MosquePhoto
            from mosques.utils.translation import translate_text_to_3_langs
            from django.utils import timezone

            # Traduction des textes
            desc_translated = translate_text_to_3_langs(obj.description or "")
            hist_translated = translate_text_to_3_langs(obj.history or "")

            # Création de la mosquée
            mosque = Mosque.objects.create(
                name=obj.name,
                country=obj.country,
                wilaya=obj.wilaya,
                city=obj.city,
                village=obj.village,
                address=obj.address,
                latitude=obj.latitude,
                longitude=obj.longitude,
                description=obj.description or "",
                history=obj.history or "",
                description_fr=desc_translated['fr'],
                description_ar=desc_translated['ar'],
                description_en=desc_translated['en'],
                history_fr=hist_translated['fr'],
                history_ar=hist_translated['ar'],
                history_en=hist_translated['en'],
                is_verified=True,
            )

            # === 3. COPIE DES PHOTOS DE LA PROPOSITION ===
            photo_count = 0

            # Récupération des photos liées via le modèle PropositionPhoto
            photos_a_copier = obj.proposition_photos.all()

            for prop_photo in photos_a_copier:
                MosquePhoto.objects.create(
                    mosque=mosque,
                    image=prop_photo.image,  # Copie la référence Cloudinary
                    uploaded_by=f"Contributeur ({obj.contributor_email or 'Anonyme'})",
                    is_approved=True,
                )
                photo_count += 1

            # Mise à jour de la photo principale de la mosquée avec la première photo
            if photos_a_copier.exists():
                mosque.main_photo = photos_a_copier.first().image
                mosque.save()

            # Marquer la proposition comme approuvée
            obj.status = 'approved'
            obj.reviewed_at = timezone.now()
            obj.save()

            # Message pour l'admin
            self.message_user(
                request,
                f"✅ Mosquée '{obj.name}' créée avec {photo_count} photo(s) !"
            )

            return redirect('admin:mosques_mosque_change', mosque.id)

        # Si sauvegarde normale
        return super().response_change(request, obj)
