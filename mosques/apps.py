from django.apps import AppConfig

class MosquesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mosques'  # ← Doit être 'mosques' (pas 'mosques.apps')
    label = 'mosques'  # ← Optionnel, mais peut aider