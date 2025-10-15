# Guide de Déploiement Gratuit sur Render

## 🚀 Déploiement sur Render (Recommandé)

### Étape 1: Préparation
1. **Créez un compte sur [Render.com](https://render.com)**
2. **Connectez votre compte GitHub** à Render
3. **Poussez votre code sur GitHub** :
   ```bash
   git add .
   git commit -m "Préparation pour le déploiement"
   git push origin main
   ```

### Étape 2: Créer un service Web sur Render
1. **Allez sur [Render Dashboard](https://dashboard.render.com)**
2. **Cliquez sur "New +" → "Web Service"**
3. **Connectez votre repository GitHub**
4. **Configurez le service** :
   - **Name**: `barber-appointment-system`
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn barber.wsgi --bind 0.0.0.0:$PORT`

### Étape 3: Ajouter une base de données PostgreSQL
1. **Cliquez sur "New +" → "PostgreSQL"**
2. **Configurez la base** :
   - **Name**: `barber-database`
   - **Database**: `barberdb`
   - **User**: `barber_user`
3. **Copiez l'URL de connexion** (elle ressemble à : `postgresql://user:password@host:port/database`)

### Étape 4: Configurer les variables d'environnement
Dans votre service web, allez dans **"Environment"** et ajoutez :

```
SECRET_KEY=votre-cle-secrete-tres-longue-et-securisee
DEBUG=False
DATABASE_URL=postgresql://user:password@host:port/database
```

**Pour générer une SECRET_KEY sécurisée** :
```python
import secrets
print(secrets.token_urlsafe(50))
```

### Étape 5: Déployer
1. **Cliquez sur "Create Web Service"**
2. **Attendez que le build se termine** (5-10 minutes)
3. **Votre site sera disponible** à l'URL fournie

### Étape 6: Créer les données de base
Une fois déployé, connectez-vous à votre admin Django et exécutez :
```bash
python manage.py shell < create_production_data.py
```

Ou créez manuellement un superutilisateur :
```bash
python manage.py createsuperuser
```

## 🔧 Autres Options Gratuites

### Railway
1. **Compte sur [Railway.app](https://railway.app)**
2. **Connectez GitHub**
3. **Déployez automatiquement**
4. **Base de données PostgreSQL incluse**

### Heroku (Limité)
1. **Compte sur [Heroku.com](https://heroku.com)**
2. **Installez Heroku CLI**
3. **Déployez avec Git**

### Vercel (Pour le frontend)
Si vous voulez séparer frontend/backend :
1. **Frontend sur [Vercel.com](https://vercel.com)**
2. **Backend sur Render**

## 📋 Checklist de Déploiement

- [ ] Code poussé sur GitHub
- [ ] Service web créé sur Render
- [ ] Base de données PostgreSQL créée
- [ ] Variables d'environnement configurées
- [ ] Build réussi
- [ ] Site accessible
- [ ] Données de test créées
- [ ] Fonctionnalités testées

## 🐛 Résolution de Problèmes

### Erreur de Build
- Vérifiez les `requirements.txt`
- Vérifiez le script `build.sh`

### Erreur de Base de Données
- Vérifiez `DATABASE_URL`
- Vérifiez les migrations

### Erreur 500
- Vérifiez les logs dans Render
- Vérifiez `DEBUG=False` en production

### Images ne s'affichent pas
- Vérifiez la configuration des fichiers statiques
- Vérifiez WhiteNoise

## 🔐 Sécurité en Production

1. **Changez la SECRET_KEY** par défaut
2. **Mettez DEBUG=False**
3. **Utilisez HTTPS** (automatique sur Render)
4. **Configurez ALLOWED_HOSTS** correctement
5. **Utilisez une base de données sécurisée**

## 📊 Monitoring

Render fournit :
- **Logs en temps réel**
- **Métriques de performance**
- **Monitoring de santé**
- **Alertes par email**

## 💰 Coûts

- **Render Free Tier** : Gratuit (avec limitations)
- **PostgreSQL Free** : Gratuit (1 Go max)
- **Domaine personnalisé** : Optionnel (payant)

## 🚀 Fonctionnalités Avancées

### Déploiement Automatique
- **GitHub Webhooks** configurés automatiquement
- **Déploiement à chaque push**

### Domaine Personnalisé
1. **Achetez un domaine** (ex: Namecheap, GoDaddy)
2. **Configurez DNS** vers Render
3. **Ajoutez le domaine** dans Render

### SSL/HTTPS
- **Automatique** sur Render
- **Certificats Let's Encrypt**

## 📞 Support

- **Documentation Render** : https://render.com/docs
- **Communauté Django** : https://forum.djangoproject.com
- **Stack Overflow** : Tag `django` + `render`
