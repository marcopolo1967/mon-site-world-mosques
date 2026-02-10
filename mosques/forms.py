from django import forms
from .models import Wilaya, Proposition, MosquePhoto, Mosque


class PropositionForm(forms.ModelForm):
    """Formulaire pour proposer une nouvelle mosquée - Version épurée"""

    photo_files = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        label="Photos"
    )


    confirmation = forms.BooleanField(
        required=True,
        label="Je confirme que ces informations sont exactes à ma connaissance",
        help_text="Merci de vérifier les informations avant soumission"
    )
    class Meta:
        model = Proposition
        fields = [
            'name', 'country', 'wilaya', 'city', 'village',
            'address', 'latitude', 'longitude',  # Déplacés AVANT description
            'description', 'history',
            'contributor_email', 'photos'  # photos à la fin
        ]
        labels = {
            'name': 'Nom de la mosquée *',
            'wilaya': 'Wilaya *',
            'city': 'Ville ou commune *',
            'village': 'Village ou quartier',
            'address': 'Adresse précise',
            'description': 'Description',
            'history': 'Historique ou informations complémentaires',
            'contributor_email': 'Votre email (facultatif)',
        }
        help_texts = {
            'contributor_email': 'Pour vous contacter si besoin. Ne sera pas publié.',
        }
        widgets = {
            'wilaya': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'history': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Rendre wilaya non requis temporairement
        self.fields['wilaya'].required = False

        # Ordonner les wilayas par code
        self.fields['wilaya'].queryset = Wilaya.objects.all().order_by('code')

        # Rendre les champs requis plus visibles
        for field_name, field in self.fields.items():
            if field_name in ['name', 'city']:
                field.widget.attrs['required'] = 'required'


    def save(self, commit=True):
        # Surcharge pour gérer les photos
        proposition = super().save(commit=False)

        if commit:
            proposition.save()

            # Ici, nous gérerons les photos dans la vue
            # plutôt que dans le formulaire pour simplifier

        return proposition

    def clean(self):
        cleaned_data = super().clean()
        country = cleaned_data.get('country', '').lower()

        # Si pays = Algérie, alors wilaya devient requis
        if 'algérie' in country or 'algeria' in country or 'dz' in country:
            if not cleaned_data.get('wilaya'):
                self.add_error('wilaya', 'La wilaya est requise pour l\'Algérie')

        return cleaned_data



class MosquePhotoForm(forms.ModelForm):
    class Meta:
        model = MosquePhoto
        fields = ['image']  # On ne demande que l'image, le reste est auto


class MosqueAdminForm(forms.ModelForm):
    """Formulaire admin basique pour la Mosquée"""

    class Meta:
        model = Mosque
        fields = '__all__'  # expose tous les champs pour l’admin
