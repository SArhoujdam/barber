# BarberShop - Application de Réservation de Rendez-vous

Une application Django moderne pour la gestion des rendez-vous dans un salon de coiffure.

## 🚀 Fonctionnalités

### Pour les Clients
- **Inscription/Connexion** : Création de compte client avec informations personnelles
- **Recherche de barbiers** : Consultation des profils et spécialités des barbiers
- **Réservation en ligne** : Système de réservation avec sélection de date, heure et service
- **Gestion des rendez-vous** : Consultation, modification et annulation des rendez-vous
- **Système d'avis** : Possibilité de laisser des avis après un rendez-vous terminé

### Pour les Barbiers
- **Inscription/Connexion** : Création de compte barbier avec spécialités et expérience
- **Tableau de bord** : Vue d'ensemble des rendez-vous et statistiques
- **Gestion des horaires** : Configuration des heures de travail par jour de la semaine
- **Gestion des services** : Ajout et modification des services proposés
- **Suivi des rendez-vous** : Mise à jour du statut des rendez-vous en temps réel

### Fonctionnalités Générales
- **Interface moderne** : Design responsive avec Bootstrap 5
- **Système de notation** : Évaluation des barbiers par les clients
- **Gestion des conflits** : Vérification automatique des créneaux disponibles
- **Administration** : Interface d'administration Django complète

## 🛠️ Installation

### Prérequis
- Python 3.8+
- Django 5.2+
- SQLite (par défaut)

### Étapes d'installation

1. **Cloner le projet**
```bash
git clone <url-du-repo>
cd barber
```

2. **Installer les dépendances**
```bash
pip install django
```

3. **Appliquer les migrations**
```bash
python manage.py migrate
```

4. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

5. **Charger les données de test (optionnel)**
```bash
python create_test_data.py
```

6. **Lancer le serveur de développement**
```bash
python manage.py runserver
```

7. **Accéder à l'application**
- Site web : http://127.0.0.1:8000/
- Administration : http://127.0.0.1:8000/admin/

## 👥 Comptes de Test

Après avoir exécuté `create_test_data.py`, vous pouvez utiliser ces comptes :

### Administrateur
- **Nom d'utilisateur** : admin
- **Mot de passe** : (défini lors de la création)

### Barbiers
- **Nom d'utilisateur** : barber1 / **Mot de passe** : password123
- **Nom d'utilisateur** : barber2 / **Mot de passe** : password123

### Clients
- **Nom d'utilisateur** : client1 / **Mot de passe** : password123
- **Nom d'utilisateur** : client2 / **Mot de passe** : password123

## 📱 Utilisation

### Pour un Client

1. **S'inscrire** : Créer un compte client avec vos informations
2. **Choisir un barbier** : Consulter la liste des barbiers et leurs profils
3. **Réserver** : Sélectionner un service, une date et une heure disponible
4. **Gérer** : Consulter vos rendez-vous, les modifier ou les annuler
5. **Évaluer** : Laisser un avis après un rendez-vous terminé

### Pour un Barbier

1. **S'inscrire** : Créer un compte barbier avec vos spécialités
2. **Configurer** : Définir vos horaires de travail et services
3. **Gérer** : Suivre vos rendez-vous via le tableau de bord
4. **Mettre à jour** : Changer le statut des rendez-vous (en cours, terminé, etc.)

## 🏗️ Architecture

### Modèles Principaux
- **Barber** : Profil des barbiers avec spécialités et disponibilité
- **Client** : Profil des clients avec informations personnelles
- **Service** : Services proposés (coupe, barbe, etc.)
- **Appointment** : Rendez-vous avec statut et gestion des conflits
- **Review** : Avis des clients sur les barbiers
- **WorkingHours** : Horaires de travail des barbiers

### Technologies Utilisées
- **Backend** : Django 5.2, Python
- **Frontend** : HTML5, CSS3, Bootstrap 5, JavaScript
- **Base de données** : SQLite (développement)
- **Authentification** : Django Auth System

## 🔧 Configuration

### Variables d'environnement
Créer un fichier `.env` pour la production :
```env
SECRET_KEY=votre-clé-secrète
DEBUG=False
ALLOWED_HOSTS=votre-domaine.com
```

### Base de données
Pour utiliser PostgreSQL en production :
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'barbershop',
        'USER': 'votre_utilisateur',
        'PASSWORD': 'votre_mot_de_passe',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 📝 API Endpoints

- `GET /api/available-times/<barber_id>/<date>/` : Obtenir les heures disponibles pour un barbier

## 🚀 Déploiement

### Heroku
1. Créer un fichier `requirements.txt`
2. Créer un fichier `Procfile`
3. Configurer les variables d'environnement
4. Déployer via Git

### Docker
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou problème :
- Créer une issue sur GitHub
- Contacter l'équipe de développement

## 🔮 Fonctionnalités Futures

- [ ] Notifications par email/SMS
- [ ] Paiement en ligne
- [ ] Application mobile
- [ ] Système de fidélité
- [ ] Gestion des stocks de produits
- [ ] Intégration avec Google Calendar
- [ ] Chat en temps réel
- [ ] Système de rappels automatiques

---

**BarberShop** - Votre salon de coiffure connecté ! 💇‍♂️✨

