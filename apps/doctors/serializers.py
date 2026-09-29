from rest_framework import serializers
from .models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    """Serializer for Doctor model with validation for uniqueness and formats."""

    class Meta:
        model = Doctor
        fields = [
            'id',
            'name',
            'specialization',
            'license_number',
            'contact_number',
            'email',
            'years_of_experience',
            'hospital_affiliation',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        trimmed = value.strip()
        if not trimmed:
            raise serializers.ValidationError('Doctor name cannot be blank.')
        return trimmed

    def validate_specialization(self, value):
        trimmed = value.strip()
        if not trimmed:
            raise serializers.ValidationError('Specialization cannot be blank.')
        return trimmed

    def validate_license_number(self, value):
        trimmed = value.strip().upper()
        if not trimmed:
            raise serializers.ValidationError('Medical license number cannot be blank.')
        # Check uniqueness excluding self if update
        queryset = Doctor.objects.filter(license_number__iexact=trimmed)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('A doctor with this license number already exists.')
        return trimmed

    def validate_email(self, value):
        normalized = value.strip().lower()
        queryset = Doctor.objects.filter(email__iexact=normalized)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('A doctor with this email address already exists.')
        return normalized
