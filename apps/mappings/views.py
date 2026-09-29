from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from apps.patients.models import Patient
from .models import PatientDoctorMapping
from .serializers import (
    MappingCreateSerializer,
    MappingDetailSerializer,
    AssignedDoctorItemSerializer,
    NestedPatientSerializer,
)


class MappingListCreateView(APIView):
    """
    List all patient-doctor mappings or assign a doctor to a patient.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: MappingDetailSerializer(many=True)},
        tags=['Mappings'],
        summary='Retrieve all patient-doctor mappings',
    )
    def get(self, request):
        if request.user.is_staff:
            mappings = PatientDoctorMapping.objects.all().select_related('patient', 'doctor')
        else:
            mappings = PatientDoctorMapping.objects.filter(
                patient__created_by=request.user
            ).select_related('patient', 'doctor')

        serializer = MappingDetailSerializer(mappings, many=True)
        return Response(
            {
                'success': True,
                'count': mappings.count(),
                'data': serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=MappingCreateSerializer,
        responses={
            201: OpenApiResponse(
                description='Doctor assigned to patient successfully.',
                response=MappingDetailSerializer,
            ),
            400: OpenApiResponse(description='Validation error or duplicate assignment.'),
        },
        tags=['Mappings'],
        summary='Assign a doctor to a patient',
    )
    def post(self, request):
        serializer = MappingCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        mapping = serializer.save()
        return Response(
            {
                'success': True,
                'message': f'Doctor "{mapping.doctor.name}" successfully assigned to Patient "{mapping.patient.name}".',
                'data': MappingDetailSerializer(mapping).data,
            },
            status=status.HTTP_201_CREATED,
        )


class PatientDoctorMappingDetailView(APIView):
    """
    Retrieve doctors assigned to a specific patient, or remove a doctor mapping.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(description='List of doctors assigned to the specified patient.'),
            404: OpenApiResponse(description='Patient not found or unauthorized.'),
        },
        tags=['Mappings'],
        summary='Get all doctors assigned to a specific patient',
    )
    def get(self, request, pk):
        """
        GET /api/mappings/<patient_id>/
        Returns all doctors assigned to the patient with id = pk.
        """
        # Validate patient exists and belongs to the user
        patient = Patient.objects.filter(pk=pk)
        if not request.user.is_staff:
            patient = patient.filter(created_by=request.user)

        patient_instance = patient.first()
        if not patient_instance:
            # Fallback check: in case pk was a mapping ID instead
            mapping = PatientDoctorMapping.objects.filter(pk=pk)
            if not request.user.is_staff:
                mapping = mapping.filter(patient__created_by=request.user)
            mapping_instance = mapping.first()
            if mapping_instance:
                return Response(
                    {
                        'success': True,
                        'data': MappingDetailSerializer(mapping_instance).data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {
                    'success': False,
                    'status_code': 404,
                    'message': f'Patient with ID {pk} not found or you do not have permission to view it.',
                    'errors': None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        mappings = PatientDoctorMapping.objects.filter(
            patient=patient_instance
        ).select_related('doctor')

        serialized_doctors = AssignedDoctorItemSerializer(mappings, many=True).data

        return Response(
            {
                'success': True,
                'patient': NestedPatientSerializer(patient_instance).data,
                'assigned_doctors_count': len(serialized_doctors),
                'doctors': serialized_doctors,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        responses={
            200: OpenApiResponse(description='Doctor removed from patient successfully.'),
            404: OpenApiResponse(description='Mapping not found or unauthorized.'),
        },
        tags=['Mappings'],
        summary='Remove a doctor from a patient (delete mapping)',
    )
    def delete(self, request, pk):
        """
        DELETE /api/mappings/<id>/
        Removes a doctor mapping with ID = pk.
        """
        mapping_qs = PatientDoctorMapping.objects.filter(pk=pk)
        if not request.user.is_staff:
            mapping_qs = mapping_qs.filter(patient__created_by=request.user)

        mapping = mapping_qs.first()
        if not mapping:
            return Response(
                {
                    'success': False,
                    'status_code': 404,
                    'message': f'Mapping with ID {pk} not found or you do not have permission to delete it.',
                    'errors': None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        doctor_name = mapping.doctor.name
        patient_name = mapping.patient.name
        mapping.delete()

        return Response(
            {
                'success': True,
                'message': f'Doctor "{doctor_name}" was successfully removed from Patient "{patient_name}".',
            },
            status=status.HTTP_200_OK,
        )
