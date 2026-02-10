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

# 3️⃣ Tenter d'appliquer les migrations (échoue silencieusement si la DB n'est pas encore configurée, comme au tout premier déploiement)
echo "🗄️  Vérification et application des migrations..."
if python manage.py showmigrations --plan 2>/dev/null | grep -q "\[ \]"; then
    echo "   ➡️  Migrations en attente détectées. Application..."
    python manage.py migrate
else
    echo "   ⏭️  Aucune migration en attente ou base de données non configurée."
fi

echo "✅ Build terminé !"
