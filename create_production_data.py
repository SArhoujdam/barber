#!/usr/bin/env python
"""
Script pour créer des données de base en production
"""

import os
import django
from datetime import date, time, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barber.settings')
django.setup()

from django.contrib.auth.models import User
from reservations.models import Barber, Client, Service, WorkingHours

def create_superuser():
    """Créer un superutilisateur s'il n'existe pas"""
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@barbershop.com',
            password='admin123'
        )
        print("Superutilisateur créé: admin / admin123")

def create_demo_barber():
    """Créer un barbier de démonstration"""
    user, created = User.objects.get_or_create(
        username='demo_barber',
        defaults={
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'email': 'demo@barbershop.com'
        }
    )
    if created:
        user.set_password('demo123')
        user.save()
    
    barber, created = Barber.objects.get_or_create(
        user=user,
        defaults={
            'name': 'Jean Dupont',
            'phone': '0123456789',
            'email': 'demo@barbershop.com',
            'speciality': 'Coupe moderne et barbe',
            'experience_years': 5,
            'bio': 'Spécialiste en coupes modernes',
            'is_available': True
        }
    )
    
    if created:
        print("Barbier de démonstration créé")
    
    return barber

def create_demo_services(barber):
    """Créer des services de démonstration"""
    services = [
        {
            'name': 'Coupe homme',
            'description': 'Coupe de cheveux moderne',
            'duration': timedelta(hours=1),
            'price': 25.00
        },
        {
            'name': 'Coupe + Barbe',
            'description': 'Coupe complète avec taille de barbe',
            'duration': timedelta(hours=1, minutes=30),
            'price': 35.00
        },
        {
            'name': 'Taille de barbe',
            'description': 'Taille et entretien de la barbe',
            'duration': timedelta(minutes=30),
            'price': 15.00
        }
    ]
    
    for service_data in services:
        service, created = Service.objects.get_or_create(
            barber=barber,
            name=service_data['name'],
            defaults=service_data
        )
        if created:
            print(f"Service créé: {service_data['name']}")

def create_working_hours(barber):
    """Créer les horaires de travail"""
    days = [0, 1, 2, 3, 4, 5]  # Lundi à Samedi
    
    for day in days:
        working_hour, created = WorkingHours.objects.get_or_create(
            barber=barber,
            day_of_week=day,
            defaults={
                'start_time': time(9, 0),
                'end_time': time(18, 0),
                'is_working': True
            }
        )
        if created:
            day_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
            print(f"Horaire créé: {day_names[day]}")

if __name__ == '__main__':
    try:
        print("Création des données de production...")
        
        # Créer le superutilisateur
        create_superuser()
        
        # Créer le barbier de démonstration
        barber = create_demo_barber()
        
        # Créer les services
        create_demo_services(barber)
        
        # Créer les horaires
        create_working_hours(barber)
        
        print("\n✅ Données de production créées avec succès!")
        print("\nComptes disponibles:")
        print("- Admin: admin / admin123")
        print("- Barbier: demo_barber / demo123")
        
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
