from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import time, timedelta
import uuid


class Barber(models.Model):
    """Modèle pour représenter un barbier"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='barber_profile')
    name = models.CharField(max_length=100, verbose_name="Nom")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    email = models.EmailField(verbose_name="Email")
    speciality = models.CharField(max_length=200, verbose_name="Spécialité")
    experience_years = models.PositiveIntegerField(verbose_name="Années d'expérience")
    bio = models.TextField(blank=True, verbose_name="Biographie")
    profile_image = models.ImageField(upload_to='barbers/', blank=True, null=True, verbose_name="Photo de profil")
    is_available = models.BooleanField(default=True, verbose_name="Disponible")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Barbier"
        verbose_name_plural = "Barbiers"
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        """Calcule la note moyenne du barbier"""
        reviews = self.reviews.all()
        if reviews.exists():
            return sum(review.rating for review in reviews) / reviews.count()
        return 0


class Service(models.Model):
    """Modèle pour représenter les services proposés"""
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='services', verbose_name="Barbier")
    name = models.CharField(max_length=100, verbose_name="Nom du service")
    description = models.TextField(verbose_name="Description")
    duration = models.DurationField(verbose_name="Durée")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Prix")
    image = models.ImageField(upload_to='services/', blank=True, null=True, verbose_name="Image")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.price}€"


class Client(models.Model):
    """Modèle pour représenter un client"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    profile_image = models.ImageField(upload_to='clients/', blank=True, null=True, verbose_name="Photo de profil")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    address = models.TextField(blank=True, verbose_name="Adresse")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Date de naissance")
    preferences = models.TextField(blank=True, verbose_name="Préférences")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Appointment(models.Model):
    """Modèle pour représenter un rendez-vous"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmé'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
        ('no_show', 'Absent'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='appointments', verbose_name="Client")
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='appointments', verbose_name="Barbier")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='appointments', verbose_name="Service")
    appointment_date = models.DateField(verbose_name="Date du rendez-vous")
    appointment_time = models.TimeField(verbose_name="Heure du rendez-vous")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    notes = models.TextField(blank=True, verbose_name="Notes")
    total_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Prix total")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Rendez-vous"
        verbose_name_plural = "Rendez-vous"
        ordering = ['appointment_date', 'appointment_time']
        unique_together = ['barber', 'appointment_date', 'appointment_time']

    def __str__(self):
        return f"{self.client} - {self.barber} - {self.appointment_date} {self.appointment_time}"

    @property
    def appointment_datetime(self):
        """Retourne la date et l'heure combinées"""
        if self.appointment_date and self.appointment_time:
            dt = timezone.datetime.combine(self.appointment_date, self.appointment_time)
            # S'assurer que le datetime a une timezone
            if dt.tzinfo is None:
                dt = timezone.make_aware(dt)
            return dt
        return None

    @property
    def end_time(self):
        """Calcule l'heure de fin du rendez-vous"""
        if self.appointment_date and self.appointment_time and self.service:
            start_time = timezone.datetime.combine(self.appointment_date, self.appointment_time)
            # S'assurer que le datetime a une timezone
            if start_time.tzinfo is None:
                start_time = timezone.make_aware(start_time)
            return start_time + self.service.duration
        return None

    def is_past(self):
        """Vérifie si le rendez-vous est dans le passé"""
        appointment_datetime = self.appointment_datetime
        if appointment_datetime:
            now = timezone.now()
            # S'assurer que les deux datetimes ont la même timezone
            if appointment_datetime.tzinfo is None:
                appointment_datetime = timezone.make_aware(appointment_datetime)
            return appointment_datetime < now
        return False

    def can_be_cancelled(self):
        """Vérifie si le rendez-vous peut être annulé"""
        appointment_datetime = self.appointment_datetime
        if appointment_datetime:
            now = timezone.now()
            # S'assurer que les deux datetimes ont la même timezone
            if appointment_datetime.tzinfo is None:
                appointment_datetime = timezone.make_aware(appointment_datetime)
            # Peut être annulé jusqu'à 2 heures avant le rendez-vous
            return (appointment_datetime - now).total_seconds() > 7200 and self.status in ['pending', 'confirmed']
        return False


class Review(models.Model):
    """Modèle pour les avis des clients"""
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='reviews', verbose_name="Client")
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='reviews', verbose_name="Barbier")
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='review', verbose_name="Rendez-vous")
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Note"
    )
    comment = models.TextField(verbose_name="Commentaire")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.client} - {self.barber} - {self.rating}/5"


class WorkingHours(models.Model):
    """Modèle pour les heures de travail des barbiers"""
    DAY_CHOICES = [
        (0, 'Lundi'),
        (1, 'Mardi'),
        (2, 'Mercredi'),
        (3, 'Jeudi'),
        (4, 'Vendredi'),
        (5, 'Samedi'),
        (6, 'Dimanche'),
    ]

    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='working_hours', verbose_name="Barbier")
    day_of_week = models.PositiveIntegerField(choices=DAY_CHOICES, verbose_name="Jour de la semaine")
    start_time = models.TimeField(verbose_name="Heure de début")
    end_time = models.TimeField(verbose_name="Heure de fin")
    is_working = models.BooleanField(default=True, verbose_name="Travaille ce jour")

    class Meta:
        verbose_name = "Horaire de travail"
        verbose_name_plural = "Horaires de travail"
        unique_together = ['barber', 'day_of_week']

    def __str__(self):
        return f"{self.barber} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"

