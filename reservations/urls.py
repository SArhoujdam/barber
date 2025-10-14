from django.urls import path
from . import views

urlpatterns = [
    # Pages publiques
    path('', views.home, name='home'),
    path('barbers/', views.barber_list, name='barber_list'),
    path('barber/<int:barber_id>/', views.barber_detail, name='barber_detail'),
    
    # Inscription
    path('register/client/', views.register_client, name='register_client'),
    path('register/barber/', views.register_barber, name='register_barber'),
    
    # Rendez-vous
    path('book/<int:barber_id>/', views.book_appointment, name='book_appointment'),
    path('appointments/', views.client_appointments, name='client_appointments'),
    path('appointment/<uuid:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('appointment/<uuid:appointment_id>/review/', views.add_review, name='add_review'),
    
    # Tableau de bord barbier
    path('barber/dashboard/', views.barber_dashboard, name='barber_dashboard'),
    path('barber/appointments/', views.barber_appointments, name='barber_appointments'),
    path('barber/appointment/<uuid:appointment_id>/update-status/', views.update_appointment_status, name='update_appointment_status'),
    path('barber/working-hours/', views.manage_working_hours, name='manage_working_hours'),
    path('barber/services/', views.manage_services, name='manage_services'),
    path('barber/services/<int:service_id>/edit/', views.edit_service, name='edit_service'),
    path('barber/services/<int:service_id>/delete/', views.delete_service, name='delete_service'),
    # QR Code
    path('barber/<int:barber_id>/qr/', views.barber_qr_code, name='barber_qr_code'),
    path('qr/<int:barber_id>/', views.qr_landing, name='qr_landing'),
    
    # Profile photos
    path('profile/barber/photo/', views.change_barber_profile_photo, name='change_barber_profile_photo'),
    path('profile/client/photo/', views.change_client_profile_photo, name='change_client_profile_photo'),
    
    # Profile editing
    path('profile/barber/edit/', views.edit_barber_profile, name='edit_barber_profile'),
    path('profile/client/edit/', views.edit_client_profile, name='edit_client_profile'),
    # Déconnexion
      path('logout/', views.logout, name='app_logout'),
    # API
    path('api/available-times/<int:barber_id>/<str:appointment_date>/', views.get_available_times, name='get_available_times'),
]

