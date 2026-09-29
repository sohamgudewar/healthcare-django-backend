from rest_framework import serializers
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    """Serializer for Patient model with validation and read-only ownership."""

    created_by_email = serializers.ReadOnlyField(source='created_by.email')
    created_by_name = serializers.ReadOnlyField(source='created_by.name')

    class Meta:
        model = Patient
        fields = [
            'id',
            'name',
            'date_of_birth',
            'age',
            'gender',
            'contact_number',
            'email',
            'address',
            'medical_history',
            'created_by',
            'created_by_email',
            'created_by_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_by',
            'created_by_email',
            'created_by_name',
            'created_at',
            'updated_at',
        ]

    def validate_name(self, value):
        trimmed = value.strip()
        if not trimmed:
            raise serializers.ValidationError('Patient name cannot be blank.')
        return trimmed

    def validate_contact_number(self, value):
        trimmed = value.strip()
        if not trimmed:
            raise serializers.ValidationError('Contact number is required.')
        # Strip common formatting characters and check minimum length
        cleaned = ''.join(c for c in trimmed if c.isdigit() or c == '+')
        if len(cleaned) < 7:
            raise serializers.ValidationError('Please provide a valid contact number.')
        return trimmed
