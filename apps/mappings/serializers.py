from rest_framework import serializers
from apps.patients.models import Patient
from apps.doctors.models import Doctor
from .models import PatientDoctorMapping


class NestedPatientSerializer(serializers.ModelSerializer):
    """Compact Patient representation for mapping outputs."""

    class Meta:
        model = Patient
        fields = ['id', 'name', 'age', 'gender', 'contact_number']


class NestedDoctorSerializer(serializers.ModelSerializer):
    """Compact Doctor representation for mapping outputs."""

    class Meta:
        model = Doctor
        fields = ['id', 'name', 'specialization', 'license_number', 'contact_number', 'email']


class MappingDetailSerializer(serializers.ModelSerializer):
    """Serializer displaying full details of a patient-doctor mapping."""

    patient = NestedPatientSerializer(read_only=True)
    doctor = NestedDoctorSerializer(read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = ['id', 'patient', 'doctor', 'notes', 'assigned_date']
        read_only_fields = ['id', 'patient', 'doctor', 'assigned_date']


class MappingCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new patient-doctor mapping.
    Validates patient ownership, doctor existence, and prevents duplicate mappings.
    """

    patient_id = serializers.IntegerField(
        required=True,
        help_text='ID of the patient (must be owned by the authenticated user).',
    )
    doctor_id = serializers.IntegerField(
        required=True,
        help_text='ID of the doctor to assign.',
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        default='',
        help_text='Optional consultation notes or assignment rationale.',
    )

    def validate(self, attrs):
        user = self.context['request'].user
        patient_id = attrs['patient_id']
        doctor_id = attrs['doctor_id']

        # 1. Validate Patient existence and ownership
        try:
            patient = Patient.objects.get(pk=patient_id)
        except Patient.DoesNotExist:
            raise serializers.ValidationError({'patient_id': 'Patient not found.'})

        if not user.is_staff and patient.created_by != user:
            raise serializers.ValidationError(
                {'patient_id': 'You do not have permission to assign doctors to this patient.'}
            )

        # 2. Validate Doctor existence
        try:
            doctor = Doctor.objects.get(pk=doctor_id)
        except Doctor.DoesNotExist:
            raise serializers.ValidationError({'doctor_id': 'Doctor not found.'})

        # 3. Prevent duplicate mapping
        if PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor).exists():
            raise serializers.ValidationError(
                {'detail': f'Doctor "{doctor.name}" is already assigned to Patient "{patient.name}".'}
            )

        attrs['patient_instance'] = patient
        attrs['doctor_instance'] = doctor
        return attrs

    def create(self, validated_data):
        mapping = PatientDoctorMapping.objects.create(
            patient=validated_data['patient_instance'],
            doctor=validated_data['doctor_instance'],
            notes=validated_data.get('notes', ''),
        )
        return mapping


class AssignedDoctorItemSerializer(serializers.ModelSerializer):
    """Displays doctor information within a patient's mapping list."""

    mapping_id = serializers.IntegerField(source='id', read_only=True)
    doctor = NestedDoctorSerializer(read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = ['mapping_id', 'doctor', 'notes', 'assigned_date']
