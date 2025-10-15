#!/usr/bin/env python
"""
Script pour créer des données de test pour l'application BarberShop
"""
import os
import sys
import django
from datetime import date, time, timedelta
from django.utils import timezone

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barber.settings')
django.setup()

from django.contrib.auth.models import User
from reservations.models import Barber, Client, Service, Appointment, Review, WorkingHours

def create_test_data():
    print("Création des données de test...")
    
    # Créer des utilisateurs de test
    print("1. Création des utilisateurs...")
    
    # Vérifier si les utilisateurs existent déjà
    if User.objects.filter(username='slimane').exists():
        print("Utilisateurs déjà créés, suppression des anciennes données...")
        User.objects.filter(username__in=['slimane', 'barber1', 'barber2', 'client1', 'client2']).delete()
    
    # Barbiers
    barber1_user = User.objects.create_user(
        username='slimane',
        email='slimane@barbershop.fr',
        password='password123',
        first_name='Slimane',
        last_name='Arhoujdam'
    )
    
    barber2_user = User.objects.create_user(
        username='barber2',
        email='barber2@barbershop.fr',
        password='password123',
        first_name='Pierre',
        last_name='Martin'
    )
    
    # Clients
    client1_user = User.objects.create_user(
        username='client1',
        email='client1@example.com',
        password='password123',
        first_name='Marie',
        last_name='Durand'
    )
    
    client2_user = User.objects.create_user(
        username='client2',
        email='client2@example.com',
        password='password123',
        first_name='Paul',
        last_name='Bernard'
    )
    
    # Créer les profils
    print("2. Création des profils...")
    
    barber1 = Barber.objects.create(
        user=barber1_user,
        name="Slimane Arhoujdam",
        phone="01 23 45 67 89",
        email="slimane@barbershop.fr",
        speciality="Coupe moderne, Barbe, Coiffure homme",
        experience_years=8,
        bio="Passionné de coiffure depuis plus de 8 ans, je me spécialise dans les coupes modernes et l'entretien de la barbe.",
        is_available=True
    )
    
    barber2 = Barber.objects.create(
        user=barber2_user,
        name="Pierre Martin",
        phone="01 23 45 67 90",
        email="barber2@barbershop.fr",
        speciality="Coupe classique, Shampooing, Soins",
        experience_years=12,
        bio="Avec 12 ans d'expérience, je maîtrise toutes les techniques de coiffure classique et moderne.",
        is_available=True
    )
    
    client1 = Client.objects.create(
        user=client1_user,
        phone="06 12 34 56 78",
        address="123 Rue de la Paix, Paris",
        birth_date=date(1990, 5, 15)
    )
    
    client2 = Client.objects.create(
        user=client2_user,
        phone="06 12 34 56 79",
        address="456 Avenue des Champs, Paris",
        birth_date=date(1985, 8, 22)
    )
    
    # Créer les services
    print("3. Création des services...")
    
    services = [
        {
            'name': 'Coupe homme',
            'description': 'Coupe de cheveux moderne pour homme avec shampoing et brushing',
            'duration': timedelta(hours=1),
            'price': 25.00
        },
        {
            'name': 'Coupe + Barbe',
            'description': 'Coupe de cheveux + taille de barbe complète',
            'duration': timedelta(hours=1, minutes=30),
            'price': 35.00
        },
        {
            'name': 'Shampooing + Brushing',
            'description': 'Shampooing professionnel avec brushing et coiffage',
            'duration': timedelta(minutes=45),
            'price': 20.00
        },
        {
            'name': 'Taille de barbe',
            'description': 'Taille et entretien de la barbe avec cire',
            'duration': timedelta(minutes=30),
            'price': 15.00
        },
        {
            'name': 'Coupe premium',
            'description': 'Coupe haut de gamme avec soins et finitions',
            'duration': timedelta(hours=1, minutes=45),
            'price': 45.00
        }
    ]
    
    created_services = []
    for i, service_data in enumerate(services):
        # Associer les services aux barbiers (alternance)
        service_data['barber'] = barber1 if i % 2 == 0 else barber2
        service = Service.objects.create(**service_data)
        created_services.append(service)
    
    # Créer les horaires de travail
    print("4. Création des horaires de travail...")
    
    days = [
        (0, 'Lundi'),
        (1, 'Mardi'),
        (2, 'Mercredi'),
        (3, 'Jeudi'),
        (4, 'Vendredi'),
        (5, 'Samedi'),
        (6, 'Dimanche')
    ]
    
    for barber in [barber1, barber2]:
        for day_num, day_name in days:
            if day_num == 6:  # Dimanche - fermé
                WorkingHours.objects.create(
                    barber=barber,
                    day_of_week=day_num,
                    start_time=time(9, 0),
                    end_time=time(17, 0),
                    is_working=False
                )
            else:
                WorkingHours.objects.create(
                    barber=barber,
                    day_of_week=day_num,
                    start_time=time(9, 0),
                    end_time=time(18, 0),
                    is_working=True
                )
    
    # Créer des rendez-vous de test
    print("5. Création des rendez-vous...")
    
    today = date.today()
    
    # Rendez-vous passés (terminés)
    past_appointments = [
        {
            'client': client1,
            'barber': barber1,
            'service': created_services[0],
            'appointment_date': today - timedelta(days=7),
            'appointment_time': time(10, 0),
            'status': 'completed',
            'total_price': 25.00,
            'notes': 'Première visite, très satisfait'
        },
        {
            'client': client2,
            'barber': barber2,
            'service': created_services[1],
            'appointment_date': today - timedelta(days=5),
            'appointment_time': time(14, 0),
            'status': 'completed',
            'total_price': 35.00,
            'notes': 'Coupe + barbe, excellent travail'
        }
    ]
    
    for apt_data in past_appointments:
        Appointment.objects.create(**apt_data)
    
    # Rendez-vous futurs
    future_appointments = [
        {
            'client': client1,
            'barber': barber1,
            'service': created_services[2],
            'appointment_date': today + timedelta(days=1),
            'appointment_time': time(11, 0),
            'status': 'confirmed',
            'total_price': 20.00,
            'notes': 'Shampooing et brushing'
        },
        {
            'client': client2,
            'barber': barber2,
            'service': created_services[4],
            'appointment_date': today + timedelta(days=3),
            'appointment_time': time(15, 0),
            'status': 'pending',
            'total_price': 45.00,
            'notes': 'Coupe premium pour événement important'
        }
    ]
    
    for apt_data in future_appointments:
        Appointment.objects.create(**apt_data)
    
    # Créer des avis
    print("6. Création des avis...")
    
    completed_appointments = Appointment.objects.filter(status='completed')
    
    reviews = [
        {
            'client': client1,
            'barber': barber1,
            'appointment': completed_appointments[0],
            'rating': 5,
            'comment': 'Excellent service ! Jean est très professionnel et à l\'écoute. Je recommande vivement.'
        },
        {
            'client': client2,
            'barber': barber2,
            'appointment': completed_appointments[1],
            'rating': 4,
            'comment': 'Très bon travail, Pierre maîtrise parfaitement son art. Seul petit bémol : un peu d\'attente.'
        }
    ]
    
    for review_data in reviews:
        Review.objects.create(**review_data)
    
    print("✅ Données de test créées avec succès !")
    print("\nComptes créés :")
    print("- Admin: admin / password123")
    print("- Barbier 1: barber1 / password123")
    print("- Barbier 2: barber2 / password123")
    print("- Client 1: client1 / password123")
    print("- Client 2: client2 / password123")

if __name__ == '__main__':
    create_test_data()



