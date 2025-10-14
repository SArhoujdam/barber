from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Barber, Client, Appointment, Service, Review, WorkingHours
from django.utils import timezone
from datetime import date, time, timedelta
import datetime


class ClientRegistrationForm(UserCreationForm):
    """Formulaire d'inscription pour les clients"""
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    phone = forms.CharField(max_length=20, required=True, label="Téléphone")
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label="Adresse")
    birth_date = forms.DateField(required=False, label="Date de naissance", 
                                widget=forms.DateInput(attrs={'type': 'date'}))
    profile_image = forms.ImageField(required=False, label="Photo de profil")

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'address', 'birth_date', 'profile_image', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Créer le profil client
            Client.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                address=self.cleaned_data['address'],
                birth_date=self.cleaned_data['birth_date'],
                profile_image=self.cleaned_data.get('profile_image')
            )
        return user


class BarberRegistrationForm(UserCreationForm):
    """Formulaire d'inscription pour les barbiers"""
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    phone = forms.CharField(max_length=20, required=True, label="Téléphone")
    speciality = forms.CharField(max_length=200, required=True, label="Spécialité")
    experience_years = forms.IntegerField(min_value=0, required=True, label="Années d'expérience")
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False, label="Biographie")
    profile_image = forms.ImageField(required=False, label="Photo de profil")

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'speciality', 'experience_years', 'bio', 'profile_image', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Créer le profil barbier
            Barber.objects.create(
                user=user,
                name=f"{user.first_name} {user.last_name}",
                phone=self.cleaned_data['phone'],
                email=self.cleaned_data['email'],
                speciality=self.cleaned_data['speciality'],
                experience_years=self.cleaned_data['experience_years'],
                bio=self.cleaned_data['bio'],
                profile_image=self.cleaned_data.get('profile_image')
            )
        return user


class AppointmentForm(forms.ModelForm):
    """Formulaire pour créer/modifier un rendez-vous"""
    appointment_date = forms.DateField(
        label="Date du rendez-vous",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=date.today()
    )
    appointment_time = forms.TimeField(
        label="Heure du rendez-vous",
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,
        label="Notes"
    )

    class Meta:
        model = Appointment
        fields = ['barber', 'service', 'appointment_date', 'appointment_time', 'notes']
        widgets = {
            'barber': forms.Select(attrs={'class': 'form-control'}),
            'service': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les barbiers disponibles
        self.fields['barber'].queryset = Barber.objects.filter(is_available=True)
        # Filtrer les services actifs
        self.fields['service'].queryset = Service.objects.filter(is_active=True)

    def clean_appointment_date(self):
        appointment_date = self.cleaned_data.get('appointment_date')
        if appointment_date and appointment_date < date.today():
            raise forms.ValidationError("La date du rendez-vous ne peut pas être dans le passé.")
        return appointment_date

    def clean(self):
        cleaned_data = super().clean()
        appointment_date = cleaned_data.get('appointment_date')
        appointment_time = cleaned_data.get('appointment_time')
        barber = cleaned_data.get('barber')
        service = cleaned_data.get('service')

        if appointment_date and appointment_time and barber and service:
            # Vérifier si le barbier travaille ce jour-là
            day_of_week = appointment_date.weekday()
            working_hours = WorkingHours.objects.filter(
                barber=barber,
                day_of_week=day_of_week,
                is_working=True
            ).first()

            if not working_hours:
                raise forms.ValidationError(f"Le barbier {barber.name} ne travaille pas ce jour-là.")

            # Vérifier si l'heure est dans les heures de travail
            if appointment_time < working_hours.start_time or appointment_time >= working_hours.end_time:
                raise forms.ValidationError(
                    f"L'heure doit être entre {working_hours.start_time} et {working_hours.end_time}."
                )

            # Vérifier si le créneau est disponible
            appointment_datetime = timezone.datetime.combine(appointment_date, appointment_time)
            end_time = appointment_datetime + service.duration

            conflicting_appointments = Appointment.objects.filter(
                barber=barber,
                appointment_date=appointment_date,
                status__in=['pending', 'confirmed', 'in_progress']
            ).exclude(pk=self.instance.pk if self.instance else None)

            for existing_appointment in conflicting_appointments:
                existing_start = existing_appointment.appointment_datetime
                existing_end = existing_appointment.end_time

                if (appointment_datetime < existing_end and end_time > existing_start):
                    raise forms.ValidationError(
                        f"Ce créneau est déjà pris. Le barbier a un rendez-vous de "
                        f"{existing_start.time()} à {existing_end.time()}."
                    )

        return cleaned_data


class ReviewForm(forms.ModelForm):
    """Formulaire pour les avis"""
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '5'}),
        label="Note (1-5)"
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        label="Commentaire"
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']


class WorkingHoursForm(forms.ModelForm):
    """Formulaire pour les heures de travail"""
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        label="Heure de début"
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        label="Heure de fin"
    )

    class Meta:
        model = WorkingHours
        fields = ['day_of_week', 'start_time', 'end_time', 'is_working']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
            'is_working': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("L'heure de début doit être antérieure à l'heure de fin.")

        return cleaned_data


class ServiceForm(forms.ModelForm):
    """Formulaire pour les services"""
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Nom du service"
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        label="Description"
    )
    duration = forms.DurationField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'HH:MM:SS'}),
        label="Durée"
    )
    price = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label="Prix (€)"
    )
    image = forms.ImageField(
        required=False,
        label="Image",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Service
        fields = ['name', 'description', 'duration', 'price', 'image', 'is_active']
        widgets = {
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BarberProfilePhotoForm(forms.ModelForm):
    """Formulaire pour changer la photo de profil du barbier"""
    profile_image = forms.ImageField(
        required=False,
        label="Photo de profil",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Barber
        fields = ['profile_image']


class ClientProfilePhotoForm(forms.ModelForm):
    """Formulaire pour changer la photo de profil du client"""
    profile_image = forms.ImageField(
        required=False,
        label="Photo de profil",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Client
        fields = ['profile_image']


class BarberProfileEditForm(forms.ModelForm):
    """Formulaire pour modifier le profil du barbier"""
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    email = forms.EmailField(required=True, label="Email")
    
    class Meta:
        model = Barber
        fields = ['name', 'phone', 'email', 'speciality', 'experience_years', 'bio', 'profile_image', 'is_available']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'speciality': forms.TextInput(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        barber = super().save(commit=False)
        if commit:
            # Mettre à jour les informations utilisateur
            barber.user.first_name = self.cleaned_data['first_name']
            barber.user.last_name = self.cleaned_data['last_name']
            barber.user.email = self.cleaned_data['email']
            barber.user.save()
            
            # Mettre à jour le nom du barbier
            barber.name = f"{self.cleaned_data['first_name']} {self.cleaned_data['last_name']}"
            barber.save()
        return barber


class ClientProfileEditForm(forms.ModelForm):
    """Formulaire pour modifier le profil du client"""
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    email = forms.EmailField(required=True, label="Email")
    
    class Meta:
        model = Client
        fields = ['phone', 'address', 'birth_date', 'preferences', 'profile_image']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'preferences': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        client = super().save(commit=False)
        if commit:
            # Mettre à jour les informations utilisateur
            client.user.first_name = self.cleaned_data['first_name']
            client.user.last_name = self.cleaned_data['last_name']
            client.user.email = self.cleaned_data['email']
            client.user.save()
            client.save()
        return client

