from django.contrib import admin
from .models import PatientDoctorMapping


@admin.register(PatientDoctorMapping)
class PatientDoctorMappingAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'assigned_date')
    list_filter = ('assigned_date', 'doctor__specialization')
    search_fields = ('patient__name', 'doctor__name', 'doctor__license_number')
    readonly_fields = ('assigned_date',)
