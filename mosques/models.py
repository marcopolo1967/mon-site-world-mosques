from django.db import models
from cloudinary.models import CloudinaryField  # ← AJOUTE CET IMPORT
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import translation
from django_countries.fields import CountryField


class Country(models.Model):

    name_fr = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100, blank=True)
    name_en = models.CharField(max_length=100, blank=True)

    code = models.CharField(max_length=10, unique=True)
    continent = models.CharField(max_length=2)
    flag_url = models.URLField(max_length=300, blank=True, default='')
    flag = models.CharField(max_length=150, default='🏳️')  # Emoji seulement

    django_country = CountryField(blank=True, null=True)  # Nom différent pour éviter conflit

    # NOUVEAUX CHAMPS À AJOUTER
    capital = models.CharField(max_length=100, blank=True)
    population = models.BigIntegerField(default=0)
    currency = models.CharField(max_length=50, blank=True)
    gdp = models.FloatField(null=True, blank=True)  # en milliards

    # Capital - versions multilingues
    capital_fr = models.CharField(max_length=100, blank=True)
    capital_ar = models.CharField(max_length=100, blank=True)
    capital_en = models.CharField(max_length=100, blank=True)

    # Devise - versions multilingues
    currency_fr = models.CharField(max_length=50, blank=True)
    currency_ar = models.CharField(max_length=50, blank=True)
    currency_en = models.CharField(max_length=50, blank=True)

    # Langue officielle - versions multilingues
    language_fr = models.CharField(max_length=100, blank=True)
    language_ar = models.CharField(max_length=100, blank=True)
    language_en = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['name_fr']

    def __str__(self):
        return f"{self.name_fr} ({self.code})"


class Wilaya(models.Model):

    country = models.ForeignKey('Country', on_delete=models.SET_NULL, null=True, blank=True, related_name='wilayas')

    """Modèle pour les 58 wilayas d'Algérie"""
    code = models.IntegerField(unique=True)
    name_fr = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = _("Wilaya")
        verbose_name_plural = _("Wilayas")
        ordering = ['code']

    def __str__(self):
        # Cette fonction détecte la langue actuelle du site
        # et renvoie le nom correspondant automatiquement
        current_lang = translation.get_language()
        if current_lang == 'ar':
            return self.name_ar
        return self.name_fr

    @property
    def name(self):
        """Permet d'utiliser {{ wilaya.name }} dans les templates"""
        return self.__str__()


class Mosque(models.Model):
    """Modèle principal pour une mosquée"""

    # === IDENTIFICATION ===
    name = models.CharField(
        max_length=255,
        verbose_name="Nom de la mosquée",
        blank=True,
        null=True
    )

    # === LOCALISATION GÉOGRAPHIQUE ===
    # 1. Le nouveau lien propre (ForeignKey)
    country_link = models.ForeignKey(
        'Country',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Pays (Sélectionner)"
    )

    #  2. Pays (avec valeur par défaut "Algérie")
    country = models.CharField("Pays", max_length=100, default="Algérie")

    international_region = models.CharField(max_length=100, blank=True, null=True)

    # Wilaya (uniquement pour l'Algérie - peut être vide pour autres pays)
    wilaya = models.ForeignKey(
        Wilaya,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Wilaya"
    )

    city = models.CharField(max_length=100, verbose_name="Ville/Commune")
    village = models.CharField(max_length=100, blank=True, verbose_name="Village")
    address = models.TextField(blank=True, verbose_name="Adresse précise")


    # === COORDONNÉES GPS (OBLIGATOIRES POUR LA CARTE) ===
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        null=True,
        blank=True,
        verbose_name="Latitude",
        help_text="Ex: 36.752887 (Alger)"
    )
    longitude = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True,
        verbose_name="Longitude",
        help_text="Ex: 3.042048 (Alger)"
    )

    # === PHOTO PRINCIPALE (Cloudinary) ===
    main_photo = CloudinaryField(
        'photo_principale',
        folder='mosquees_annuaire/',
        blank=True,
        null=True,
        help_text="Photo principale de la mosquée",
        transformation={
            'quality': 'auto:good',
            'width': 1200,
            'height': 800,
            'crop': 'limit',
            'fetch_format': 'auto'
        }
    )

    # === DESCRIPTION ET HISTORIQUE ===
    description = models.TextField(blank=True, verbose_name="Description")
    history = models.TextField(blank=True, verbose_name="Historique")


    # === MODÉRATION ET STATUT ===
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Vérifiée",
        help_text="Cocher pour afficher sur la carte"
    )

    # === DATES AUTOMATIQUES ===
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")

    class Meta:
        ordering = ['-created_at', 'wilaya', 'city', 'name']
        verbose_name = "Mosquée"
        verbose_name_plural = "Mosquées"


    def __str__(self):
        """Affichage dans l'admin"""
        location_parts = []
        if self.village:
            location_parts.append(self.village)
        location_parts.append(self.city)
        if self.wilaya:
            location_parts.append(self.wilaya.name_fr)

        location = ", ".join(location_parts)
        return f"{self.name} ({location})"

    @property
    def has_coordinates(self):
        """Vérifie si la mosquée a des coordonnées GPS"""
        return bool(self.latitude and self.longitude)

    @property
    def is_visible_on_map(self):
        """Vérifie si la mosquée doit apparaître sur la carte"""
        return self.is_verified and self.has_coordinates

    def save(self, *args, **kwargs):
        from mosques.utils.translation import translate_text_to_3_langs

        # --- 1. RÉCUPÉRATION DES VALEURS BRUTES ---
        # On utilise __dict__.get pour lire la base de données sans la magie de Django
        n_fr = (self.__dict__.get('name_fr', "") or "").strip()
        n_ar = (self.__dict__.get('name_ar', "") or "").strip()
        n_en = (self.__dict__.get('name_en', "") or "").strip()

        # --- 2. DÉTECTION DU "FAUX" FRANÇAIS ---
        # Si le formulaire est soumis en Anglais, Django copie souvent l'Anglais dans le champ FR.
        # On vérifie si n_fr est juste une copie de n_ar ou n_en.
        is_fr_fake = (n_fr == n_ar and n_ar != "") or (n_fr == n_en and n_en != "")

        # --- 3. GESTION DES NOMS ---
        # Sécurité : On bloque si vraiment rien n'est saisi
        if not n_fr and not n_ar and not n_en:
            from django.core.exceptions import ValidationError
            raise ValidationError("Vous devez remplir au moins un nom (Français, Arabe ou Anglais).")

        # On traduit si le FR est vide OU s'il contient une copie auto (fake)
        # OU si l'un des deux autres (AR/EN) est vide.
        if (not n_fr or is_fr_fake) or not n_ar or not n_en:
            # On définit la source de traduction (la première langue disponible et non suspecte)
            # Si le FR est suspect, on privilégie l'AR ou l'EN comme source.
            source_name = n_ar or n_en or n_fr

            if source_name:
                t_names = translate_text_to_3_langs(source_name)

                # On remplit le Français si il était vide ou fake
                if not n_fr or is_fr_fake: self.name_fr = t_names['fr']
                # On remplit les autres si ils sont vides
                if not n_ar: self.name_ar = t_names['ar']
                if not n_en: self.name_en = t_names['en']

        # --- 4. GESTION DE L'HISTORIQUE ET DESCRIPTION ---
        h_fr = (self.__dict__.get('history_fr', "") or "").strip()
        d_fr = (self.__dict__.get('description_fr', "") or "").strip()

        # Phrases par défaut
        def_h_ar, def_h_en = "لا يوجد تاريخ متاح حاليا", "No history available at the moment"
        def_d_ar, def_d_en = "لا يوجد وصف متاح حاليا", "No description available at the moment"

        # Traitement Histoire : Traduction si FR est saisi
        if h_fr:
            # On traduit si AR ou EN sont vides ou ont encore la phrase par défaut
            if (not self.history_ar or self.history_ar == def_h_ar) or \
                    (not self.history_en or self.history_en == def_h_en):
                t_hist = translate_text_to_3_langs(h_fr)
                self.history_ar = t_hist['ar']
                self.history_en = t_hist['en']
        else:
            # Sinon, on remet les phrases par défaut
            self.history_ar = def_h_ar
            self.history_en = def_h_en

        # Traitement Description : Traduction si FR est saisi
        if d_fr:
            # On traduit si AR ou EN sont vides ou ont encore la phrase par défaut
            if (not self.description_ar or self.description_ar == def_d_ar) or \
                    (not self.description_en or self.description_en == def_d_en):
                t_desc = translate_text_to_3_langs(d_fr)
                self.description_ar = t_desc['ar']
                self.description_en = t_desc['en']
        else:
            self.description_ar = def_d_ar
            self.description_en = def_d_en

        super().save(*args, **kwargs)

#==========================================================
#  STOCKAGE DES PROPOSTIONS DES VISITEURS
#==========================================================

class Proposition(models.Model):
    """Modèle pour les propositions des visiteurs (en attente de validation)"""

    # Données de la mosquée proposée
    name = models.CharField(max_length=255, verbose_name="Nom de la mosquée")
    wilaya = models.ForeignKey(Wilaya, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Wilaya")
    city = models.CharField(max_length=100, verbose_name="Ville/Commune")
    village = models.CharField(max_length=100, blank=True, verbose_name="Village")
    address = models.TextField(blank=True, verbose_name="Adresse précise")
    # models.py - Dans la classe Proposition, ajoutez :
    country = models.CharField("Pays", max_length=100, default="Algérie")

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        null=True,
        blank=True,
        verbose_name="Latitude"
    )
    longitude = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True,
        verbose_name="Longitude"
    )
    description = models.TextField(blank=True, verbose_name="Description")
    history = models.TextField(blank=True, verbose_name="Historique")



    # Informations du contributeur
    contributor_email = models.EmailField(blank=True, verbose_name="Email du contributeur")
    contributor_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name="Adresse IP")

    # Statut de modération
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvée'),
        ('rejected', 'Rejetée'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Statut"
    )

    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de proposition")
    reviewed_at = models.DateTimeField(blank=True, null=True, verbose_name="Date de modération")
    review_notes = models.TextField(blank=True, verbose_name="Notes du modérateur")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Proposition"
        verbose_name_plural = "Propositions"

    def __str__(self):
        return f"Proposition: {self.name} ({self.get_status_display()})"

    def approve(self):
        """Approuve la proposition et crée une mosquée"""
        from .models import Mosque

        mosque = Mosque.objects.create(
            name=self.name,
            wilaya=self.wilaya,
            city=self.city,
            village=self.village,
            address=self.address,
            description=self.description,
            history=self.history,
            is_verified=True,
        )
        self.status = 'approved'
        self.reviewed_at = timezone.now()
        self.save()
        return mosque

class PropositionPhoto(models.Model):
    proposition = models.ForeignKey(
        Proposition,
        on_delete=models.CASCADE,
        related_name='proposition_photos'  # Changer ici pour éviter le clash
    )

    image = CloudinaryField(
        'image',
        upload_preset='mosquee_standard'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo pour {self.proposition.name}"


from django.core.exceptions import ValidationError

def validate_image_size(fieldfile_obj):
    filesize = fieldfile_obj.size
    megabyte_limit = 5.0
    if filesize > megabyte_limit * 1024 * 1024:
        raise ValidationError(f"La taille maximale des photos est de {megabyte_limit}MB")


class MosquePhoto(models.Model):
    mosque = models.ForeignKey(Mosque, on_delete=models.CASCADE, related_name='photos')
    # models.py - AJOUTEZ ce champ
    image_url = models.URLField(blank=True)  # Pour stocker l'URL originale

    # Correction ici : on enlève "options=" et on met les paramètres directement
    image = CloudinaryField(
        'image',
        upload_preset='mosquee_standard',  # On le met directement ici

    )

    uploaded_by = models.CharField(max_length=100, default='Admin')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Champ pour Caption
    caption = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="Optionnel : description ou légende de la photo"
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Photo de {self.mosque.name} par {self.uploaded_by}"


# ====================================================================
# MODÈLE PROXY POUR LA VUE SPÉCIALE DES PHOTOS
# ====================================================================

class MosqueWithPhotos(Mosque):
    """Modèle proxy pour afficher uniquement les mosquées avec photos"""

    class Meta:
        proxy = True
        verbose_name = "📸 Mosque photos"
        verbose_name_plural = "📸 Mosque photos"
        app_label = 'mosques'

    def __str__(self):
        return f"{self.name} ({self.photos.count()} photos)"


