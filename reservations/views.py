from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q, Avg
from datetime import date, timedelta
from io import BytesIO
import json

from .models import Barber, Client, Appointment, Service, Review, WorkingHours
from .forms import (
    ClientRegistrationForm, BarberRegistrationForm, AppointmentForm, 
    ReviewForm, WorkingHoursForm, ServiceForm, BarberProfilePhotoForm, ClientProfilePhotoForm,
    BarberProfileEditForm, ClientProfileEditForm
)

from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect

def logout(request):
    """Logs out the user and redirects to the login page."""
    auth_logout(request)
    return redirect('login')  # replace 'login' with your actual login URL name
def home(request):
    """Page d'accueil"""
    barbers = Barber.objects.filter(is_available=True)[:6]
    services = Service.objects.filter(is_active=True)[:6]
    recent_reviews = Review.objects.select_related('client', 'barber').order_by('-created_at')[:3]
    
    context = {
        'barbers': barbers,
        'services': services,
        'recent_reviews': recent_reviews,
    }
    return render(request, 'reservations/home.html', context)


def register_client(request):
    """Inscription des clients"""
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Votre compte client a été créé avec succès!')
                return redirect('home')
    else:
        form = ClientRegistrationForm()
    return render(request, 'reservations/register_client.html', {'form': form})


def register_barber(request):
    """Inscription des barbiers"""
    if request.method == 'POST':
        form = BarberRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Votre compte barbier a été créé avec succès!')
                return redirect('barber_dashboard')
    else:
        form = BarberRegistrationForm()
    return render(request, 'reservations/register_barber.html', {'form': form})


def barber_list(request):
    """Liste des barbiers"""
    barbers = Barber.objects.filter(is_available=True).annotate(
        avg_rating=Avg('reviews__rating')
    ).order_by('-avg_rating')
    
    context = {
        'barbers': barbers,
    }
    return render(request, 'reservations/barber_list.html', context)


def barber_detail(request, barber_id):
    """Détails d'un barbier"""
    barber = get_object_or_404(Barber, id=barber_id)
    reviews = Review.objects.filter(barber=barber).order_by('-created_at')
    services = Service.objects.filter(is_active=True)
    
    # Calculer la note moyenne
    avg_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    
    context = {
        'barber': barber,
        'reviews': reviews,
        'services': services,
        'avg_rating': round(avg_rating, 1),
    }
    return render(request, 'reservations/barber_detail.html', context)


@login_required
def book_appointment(request, barber_id):
    """Réserver un rendez-vous"""
    barber = get_object_or_404(Barber, id=barber_id)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.client = request.user.client_profile
            appointment.barber = barber
            appointment.total_price = appointment.service.price
            appointment.save()
            messages.success(request, 'Votre rendez-vous a été réservé avec succès!')
            return redirect('client_appointments')
    else:
        form = AppointmentForm(initial={'barber': barber})
    
    context = {
        'form': form,
        'barber': barber,
    }
    return render(request, 'reservations/book_appointment.html', context)


@login_required
def client_appointments(request):
    """Rendez-vous du client avec position dans la file d'attente"""
    if hasattr(request.user, 'client_profile'):
        client = request.user.client_profile
        appointments = list(
            Appointment.objects.filter(client=client)
            .order_by('-appointment_date', '-appointment_time')
        )
        # Calculer la position avant le client pour les rendez-vous à venir le même jour
        for appt in appointments:
            appt.queue_position = None
            if appt.status in ['pending', 'confirmed', 'in_progress'] and not appt.is_past():
                appt.queue_position = Appointment.objects.filter(
                    barber=appt.barber,
                    appointment_date=appt.appointment_date,
                    status__in=['pending', 'confirmed', 'in_progress'],
                    appointment_time__lt=appt.appointment_time,
                ).count()
        context = {
            'appointments': appointments,
        }
    else:
        context = {
            'appointments': [],
            'upcoming_positions': {},
        }
    return render(request, 'reservations/client_appointments.html', context)


@login_required
def barber_dashboard(request):
    """Tableau de bord du barbier"""
    if not hasattr(request.user, 'barber_profile'):
        messages.error(request, 'Vous devez être un barbier pour accéder à cette page.')
        return redirect('home')
    
    barber = request.user.barber_profile
    today = date.today()
    
    # Rendez-vous d'aujourd'hui
    today_appointments = Appointment.objects.filter(
        barber=barber,
        appointment_date=today
    ).order_by('appointment_time')
    
    # Rendez-vous à venir
    upcoming_appointments = Appointment.objects.filter(
        barber=barber,
        appointment_date__gt=today
    ).order_by('appointment_date', 'appointment_time')[:10]
    
    # Statistiques
    total_appointments = Appointment.objects.filter(barber=barber).count()
    completed_appointments = Appointment.objects.filter(barber=barber, status='completed').count()
    pending_appointments = Appointment.objects.filter(barber=barber, status='pending').count()
    
    context = {
        'barber': barber,
        'today_appointments': today_appointments,
        'upcoming_appointments': upcoming_appointments,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'pending_appointments': pending_appointments,
    }
    return render(request, 'reservations/barber_dashboard.html', context)


@login_required
def update_appointment_status(request, appointment_id):
    """Mettre à jour le statut d'un rendez-vous"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in [choice[0] for choice in Appointment.STATUS_CHOICES]:
            appointment.status = new_status
            appointment.save()
            messages.success(request, f'Le statut du rendez-vous a été mis à jour: {appointment.get_status_display()}')
    
    return redirect('barber_dashboard')


@login_required
def cancel_appointment(request, appointment_id):
    """Annuler un rendez-vous"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Vérifier si le client peut annuler
    if hasattr(request.user, 'client_profile') and appointment.client == request.user.client_profile:
        if appointment.can_be_cancelled():
            appointment.status = 'cancelled'
            appointment.save()
            messages.success(request, 'Votre rendez-vous a été annulé.')
        else:
            messages.error(request, 'Ce rendez-vous ne peut plus être annulé.')
    else:
        messages.error(request, 'Vous ne pouvez pas annuler ce rendez-vous.')
    
    return redirect('client_appointments')


@login_required
def add_review(request, appointment_id):
    """Ajouter un avis"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Vérifier que le client peut laisser un avis
    if not hasattr(request.user, 'client_profile') or appointment.client != request.user.client_profile:
        messages.error(request, 'Vous ne pouvez pas laisser d\'avis pour ce rendez-vous.')
        return redirect('client_appointments')
    
    if appointment.status != 'completed':
        messages.error(request, 'Vous ne pouvez laisser un avis que pour un rendez-vous terminé.')
        return redirect('client_appointments')
    
    # Vérifier s'il n'y a pas déjà un avis
    if hasattr(appointment, 'review'):
        messages.error(request, 'Vous avez déjà laissé un avis pour ce rendez-vous.')
        return redirect('client_appointments')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.client = request.user.client_profile
            review.barber = appointment.barber
            review.appointment = appointment
            review.save()
            messages.success(request, 'Votre avis a été ajouté avec succès!')
            return redirect('client_appointments')
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'appointment': appointment,
    }
    return render(request, 'reservations/add_review.html', context)


@login_required
def manage_working_hours(request):
    """Gérer les heures de travail"""
    if not hasattr(request.user, 'barber_profile'):
        messages.error(request, 'Vous devez être un barbier pour accéder à cette page.')
        return redirect('home')
    
    barber = request.user.barber_profile
    
    if request.method == 'POST':
        form = WorkingHoursForm(request.POST)
        if form.is_valid():
            working_hours = form.save(commit=False)
            working_hours.barber = barber
            working_hours.save()
            messages.success(request, 'Les heures de travail ont été mises à jour.')
            return redirect('manage_working_hours')
    else:
        form = WorkingHoursForm()
    
    working_hours = WorkingHours.objects.filter(barber=barber).order_by('day_of_week')
    
    context = {
        'form': form,
        'working_hours': working_hours,
    }
    return render(request, 'reservations/manage_working_hours.html', context)


@login_required
def manage_services(request):
    """Gérer les services"""
    if not hasattr(request.user, 'barber_profile'):
        messages.error(request, 'Vous devez être un barbier pour accéder à cette page.')
        return redirect('home')
    
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            new_service = form.save(commit=False)
            new_service.barber = request.user.barber_profile
            new_service.save()
            messages.success(request, 'Le service a été ajouté avec succès.')
            return redirect('manage_services')
    else:
        form = ServiceForm()
    
    services = Service.objects.filter(barber=request.user.barber_profile).order_by('name')
    
    context = {
        'form': form,
        'services': services,
    }
    return render(request, 'reservations/manage_services.html', context)


@login_required
def edit_service(request, service_id):
    """Modifier un service existant."""
    if not hasattr(request.user, 'barber_profile'):
        messages.error(request, 'Vous devez être un barbier pour accéder à cette page.')
        return redirect('home')

    service = get_object_or_404(Service, id=service_id, barber=request.user.barber_profile)
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Le service a été mis à jour avec succès.')
            return redirect('manage_services')
    else:
        form = ServiceForm(instance=service)

    return render(request, 'reservations/edit_service.html', {'form': form, 'service': service})


@login_required
def delete_service(request, service_id):
    """Supprimer un service."""
    if not hasattr(request.user, 'barber_profile'):
        messages.error(request, 'Vous devez être un barbier pour accéder à cette page.')
        return redirect('home')

    service = get_object_or_404(Service, id=service_id, barber=request.user.barber_profile)
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Le service a été supprimé avec succès.')
        return redirect('manage_services')

    return render(request, 'reservations/confirm_delete_service.html', {'service': service})


@login_required
def change_barber_profile_photo(request):
    """Changer la photo de profil du barbier"""
    if not hasattr(request.user, 'barber_profile'):
        messages.error(request, 'Vous devez être un barbier pour accéder à cette page.')
        return redirect('home')
    
    barber = request.user.barber_profile
    if request.method == 'POST':
        form = BarberProfilePhotoForm(request.POST, request.FILES, instance=barber)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre photo de profil a été mise à jour avec succès.')
            return redirect('barber_dashboard')
    else:
        form = BarberProfilePhotoForm(instance=barber)
    
    return render(request, 'reservations/change_profile_photo.html', {
        'form': form, 
        'profile_type': 'barber',
        'profile': barber
    })


@login_required
def change_client_profile_photo(request):
    """Changer la photo de profil du client"""
    if not hasattr(request.user, 'client_profile'):
        messages.error(request, 'Vous devez être un client pour accéder à cette page.')
        return redirect('home')
    
    client = request.user.client_profile
    if request.method == 'POST':
        form = ClientProfilePhotoForm(request.POST, request.FILES, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre photo de profil a été mise à jour avec succès.')
            return redirect('client_appointments')
    else:
        form = ClientProfilePhotoForm(instance=client)
    
    return render(request, 'reservations/change_profile_photo.html', {
        'form': form, 
        'profile_type': 'client',
        'profile': client
    })


@login_required
def edit_barber_profile(request):
    """Modifier le profil du barbier"""
    if not hasattr(request.user, 'barber_profile'):
        messages.error(request, 'Vous devez être un barbier pour accéder à cette page.')
        return redirect('home')
    
    barber = request.user.barber_profile
    if request.method == 'POST':
        form = BarberProfileEditForm(request.POST, request.FILES, instance=barber)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès.')
            return redirect('barber_dashboard')
    else:
        form = BarberProfileEditForm(instance=barber)
    
    return render(request, 'reservations/edit_profile.html', {
        'form': form, 
        'profile_type': 'barber',
        'profile': barber
    })


@login_required
def edit_client_profile(request):
    """Modifier le profil du client"""
    if not hasattr(request.user, 'client_profile'):
        messages.error(request, 'Vous devez être un client pour accéder à cette page.')
        return redirect('home')
    
    client = request.user.client_profile
    if request.method == 'POST':
        form = ClientProfileEditForm(request.POST, request.FILES, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès.')
            return redirect('client_appointments')
    else:
        form = ClientProfileEditForm(instance=client)
    
    return render(request, 'reservations/edit_profile.html', {
        'form': form, 
        'profile_type': 'client',
        'profile': client
    })


def get_available_times(request, barber_id, appointment_date):
    """API pour obtenir les heures disponibles"""
    try:
        barber = Barber.objects.get(id=barber_id)
        appointment_date = date.fromisoformat(appointment_date)
        
        # Obtenir les heures de travail du barbier pour ce jour
        day_of_week = appointment_date.weekday()
        working_hours = WorkingHours.objects.filter(
            barber=barber,
            day_of_week=day_of_week,
            is_working=True
        ).first()
        
        if not working_hours:
            return JsonResponse({'available_times': []})
        
        # Obtenir les rendez-vous existants
        existing_appointments = Appointment.objects.filter(
            barber=barber,
            appointment_date=appointment_date,
            status__in=['pending', 'confirmed', 'in_progress']
        )
        
        # Générer les créneaux disponibles
        available_times = []
        current_time = working_hours.start_time
        end_time = working_hours.end_time
        
        while current_time < end_time:
            # Vérifier si ce créneau est libre
            is_available = True
            for appointment in existing_appointments:
                appointment_start = appointment.appointment_time
                appointment_end = appointment.end_time.time()
                
                if (current_time < appointment_end and 
                    timezone.datetime.combine(appointment_date, current_time) + timedelta(hours=1) > 
                    timezone.datetime.combine(appointment_date, appointment_start)):
                    is_available = False
                    break
            
            if is_available:
                available_times.append(current_time.strftime('%H:%M'))
            
            # Passer au créneau suivant (toutes les 30 minutes)
            current_time = (timezone.datetime.combine(appointment_date, current_time) + 
                          timedelta(minutes=30)).time()
        
        return JsonResponse({'available_times': available_times})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def barber_appointments(request):
    """Liste complète des rendez-vous pour le barbier connecté"""
    if not hasattr(request.user, 'barber_profile'):
        messages.error(request, 'Vous devez être un barbier pour accéder à cette page.')
        return redirect('home')

    barber = request.user.barber_profile
    status_filter = request.GET.get('status')
    qs = Appointment.objects.filter(barber=barber).order_by('appointment_date', 'appointment_time')
    if status_filter in [c[0] for c in Appointment.STATUS_CHOICES]:
        qs = qs.filter(status=status_filter)

    context = {
        'appointments': qs,
        'status_filter': status_filter or '',
        'status_choices': Appointment.STATUS_CHOICES,
    }
    return render(request, 'reservations/barber_appointments.html', context)


def barber_qr_code(request, barber_id):
    """Génère un QR code PNG qui pointe vers la page d'atterrissage QR du barbier."""
    try:
        import qrcode
    except ImportError:
        return HttpResponse("Le package 'qrcode' n'est pas installé.", status=500)

    # Construire l'URL absolue de la landing page
    landing_url = request.build_absolute_uri(
        redirect('qr_landing', barber_id=barber_id).url
    )

    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(landing_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return HttpResponse(buffer.getvalue(), content_type='image/png')


def qr_landing(request, barber_id):
    """Page d'atterrissage après scan du QR avec CTA pour réserver."""
    barber = get_object_or_404(Barber, id=barber_id)
    services = Service.objects.filter(is_active=True)
    context = {
        'barber': barber,
        'services': services,
    }
    return render(request, 'reservations/qr_landing.html', context)