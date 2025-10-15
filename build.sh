#!/usr/bin/env bash
# Script de build pour Render

set -o errexit

echo "Building..."

# Installer les dépendances
pip install -r requirements.txt

# Collecter les fichiers statiques
python manage.py collectstatic --noinput

# Appliquer les migrations
python manage.py migrate

echo "Build complete!"
