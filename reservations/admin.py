from django.contrib import admin
from django.utils.html import format_html
from .models import Barber, Client, Service, Appointment, Review, WorkingHours


@admin.register(Barber)
class BarberAdmin(admin.ModelAdmin):
    list_display = ['name', 'speciality', 'experience_years', 'is_available', 'average_rating_display', 'created_at']
    list_filter = ['is_available', 'experience_years', 'created_at']
    search_fields = ['name', 'speciality', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'average_rating_display']
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('user', 'name', 'phone', 'email')
        }),
        ('Informations professionnelles', {
            'fields': ('speciality', 'experience_years', 'bio', 'profile_image')
        }),
        ('Statut', {
            'fields': ('is_available',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at', 'average_rating_display'),
            'classes': ('collapse',)
        }),
    )
    
    def average_rating_display(self, obj):
        rating = obj.average_rating
        if rating > 0:
            stars = '★' * int(rating) + '☆' * (5 - int(rating))
            return format_html('<span style="color: gold;">{}</span> ({:.1f}/5)', stars, rating)
        return 'Aucun avis'
    average_rating_display.short_description = 'Note moyenne'


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'appointments_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'appointments_count']
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('user', 'phone', 'address', 'birth_date')
        }),
        ('Préférences', {
            'fields': ('preferences',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at', 'appointments_count'),
            'classes': ('collapse',)
        }),
    )
    
    def appointments_count(self, obj):
        return obj.appointments.count()
    appointments_count.short_description = 'Nombre de rendez-vous'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'barber', 'price', 'duration', 'is_active', 'appointments_count', 'created_at']
    list_filter = ['is_active', 'created_at', 'barber']
    search_fields = ['name', 'description', 'barber__name']
    readonly_fields = ['created_at', 'appointments_count']
    
    fieldsets = (
        ('Informations du service', {
            'fields': ('barber', 'name', 'description', 'price', 'duration', 'image', 'is_active')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'appointments_count'),
            'classes': ('collapse',)
        }),
    )
    
    def appointments_count(self, obj):
        return obj.appointments.count()
    appointments_count.short_description = 'Nombre de rendez-vous'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['client', 'barber', 'service', 'appointment_date', 'appointment_time', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'appointment_date', 'created_at', 'barber']
    search_fields = ['client__user__first_name', 'client__user__last_name', 'barber__name', 'service__name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'appointment_datetime_display', 'end_time_display']
    date_hierarchy = 'appointment_date'
    
    fieldsets = (
        ('Informations du rendez-vous', {
            'fields': ('id', 'client', 'barber', 'service', 'appointment_date', 'appointment_time')
        }),
        ('Détails', {
            'fields': ('status', 'total_price', 'notes')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at', 'appointment_datetime_display', 'end_time_display'),
            'classes': ('collapse',)
        }),
    )
    
    def appointment_datetime_display(self, obj):
        if obj.appointment_datetime:
            return obj.appointment_datetime.strftime('%d/%m/%Y %H:%M')
        return '-'
    appointment_datetime_display.short_description = 'Date et heure'
    
    def end_time_display(self, obj):
        if obj.end_time:
            return obj.end_time.strftime('%H:%M')
        return '-'
    end_time_display.short_description = 'Heure de fin'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['client', 'barber', 'rating', 'created_at']
    list_filter = ['rating', 'created_at', 'barber']
    search_fields = ['client__user__first_name', 'client__user__last_name', 'barber__name', 'comment']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Informations de l\'avis', {
            'fields': ('client', 'barber', 'appointment', 'rating', 'comment')
        }),
        ('Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(WorkingHours)
class WorkingHoursAdmin(admin.ModelAdmin):
    list_display = ['barber', 'day_of_week', 'start_time', 'end_time', 'is_working']
    list_filter = ['day_of_week', 'is_working', 'barber']
    search_fields = ['barber__name']
    
    fieldsets = (
        ('Informations des horaires', {
            'fields': ('barber', 'day_of_week', 'start_time', 'end_time', 'is_working')
        }),
    )


# Personnalisation de l'interface d'administration
admin.site.site_header = "BarberShop - Administration"
admin.site.site_title = "BarberShop Admin"
admin.site.index_title = "Gestion du salon de coiffure"

