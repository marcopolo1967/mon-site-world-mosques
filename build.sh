#!/usr/bin/env bash
# Script de build pour Render et dev local
# https://render.com/docs/deploy-django

set -o errexit  # Arrête le script si une commande échoue
set -o nounset  # Erreur si variable non définie

echo "🚀 Début du build..."

# 1️⃣ Installer les dépendances Python
echo "📦 Installation des dépendances..."
pip install -r requirements.txt

# 2️⃣ Collecter les fichiers statiques
echo "🖼️  Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# 3️⃣ Compiler les fichiers de traduction (AJOUTÉ)
echo "🌐 Compilation des messages de traduction..."
python manage.py compilemessages

# 4️⃣ Appliquer les migrations de base de données
echo "🗄️  Application des migrations..."
python manage.py migrate --noinput

# 5️⃣ Créer le superutilisateur marcopolo67 (s'il n'existe pas déjà)
echo "👤 Création du superutilisateur marcopolo67..."
cat > /tmp/create_superuser.py << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='marcopolo67').exists():
    User.objects.create_superuser('marcopolo67', 'jack.meyers@yahoo.fr', 'Abde67zine*#')
    print('   → Superutilisateur marcopolo67 créé avec succès.')
else:
    print('   → Le superutilisateur marcopolo67 existe déjà.')
EOF
python manage.py shell < /tmp/create_superuser.py

echo "✅ Build terminé !"