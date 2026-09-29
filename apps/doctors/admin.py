from django.contrib import admin
from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'specialization', 'license_number', 'contact_number', 'email', 'created_at')
    list_filter = ('specialization', 'created_at')
    search_fields = ('name', 'specialization', 'license_number', 'email')
    readonly_fields = ('created_at', 'updated_at')
