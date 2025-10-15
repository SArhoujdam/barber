#!/usr/bin/env python
"""
Script pour préparer le déploiement
"""

import secrets
import os

def generate_secret_key():
    """Générer une SECRET_KEY sécurisée"""
    return secrets.token_urlsafe(50)

def main():
    print("🚀 Préparation du déploiement sur Render")
    print("=" * 50)
    
    # Générer une SECRET_KEY sécurisée
    secret_key = generate_secret_key()
    print(f"🔑 SECRET_KEY générée:")
    print(f"SECRET_KEY={secret_key}")
    print()
    
    print("📋 Variables d'environnement pour Render:")
    print("-" * 40)
    print("SECRET_KEY=" + secret_key)
    print("DEBUG=False")
    print("DATABASE_URL=postgresql://user:password@host:port/database")
    print()
    
    print("📁 Fichiers créés pour le déploiement:")
    print("-" * 40)
    print("✅ runtime.txt - Version Python")
    print("✅ requirements.txt - Dépendances")
    print("✅ build.sh - Script de build")
    print("✅ Procfile - Configuration Gunicorn")
    print("✅ .gitignore - Fichiers à ignorer")
    print("✅ DEPLOYMENT_GUIDE.md - Guide complet")
    print()
    
    print("🌐 Étapes suivantes:")
    print("-" * 40)
    print("1. Créez un compte sur https://render.com")
    print("2. Connectez votre repository GitHub")
    print("3. Créez un service Web")
    print("4. Ajoutez une base PostgreSQL")
    print("5. Configurez les variables d'environnement")
    print("6. Déployez!")
    print()
    
    print("📖 Consultez DEPLOYMENT_GUIDE.md pour les détails complets")
    print()
    
    # Créer un fichier .env.local pour le test local
    with open('.env.local', 'w') as f:
        f.write(f"SECRET_KEY={secret_key}\n")
        f.write("DEBUG=True\n")
    
    print("✅ Fichier .env.local créé pour les tests locaux")
    print("⚠️  N'oubliez pas de supprimer .env.local avant de pousser sur GitHub")

if __name__ == '__main__':
    main()
