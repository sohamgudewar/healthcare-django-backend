from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Patient
from .serializers import PatientSerializer


class PatientListCreateView(APIView):
    """
    List all patients created by the authenticated user or register a new patient.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: PatientSerializer(many=True)},
        tags=['Patients'],
        summary='Retrieve all patients created by authenticated user',
    )
    def get(self, request):
        patients = Patient.objects.filter(created_by=request.user)
        serializer = PatientSerializer(patients, many=True)
        return Response(
            {
                'success': True,
                'count': patients.count(),
                'data': serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=PatientSerializer,
        responses={
            201: OpenApiResponse(description='Patient created successfully.', response=PatientSerializer),
            400: OpenApiResponse(description='Validation error.'),
        },
        tags=['Patients'],
        summary='Add a new patient record',
    )
    def post(self, request):
        serializer = PatientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        patient = serializer.save(created_by=request.user)
        return Response(
            {
                'success': True,
                'message': 'Patient record created successfully.',
                'data': PatientSerializer(patient).data,
            },
            status=status.HTTP_201_CREATED,
        )


class PatientDetailView(APIView):
    """
    Retrieve, update, or delete a specific patient record owned by the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get_patient(self, request, pk):
        return get_object_or_404(Patient, pk=pk, created_by=request.user)

    @extend_schema(
        responses={
            200: PatientSerializer,
            404: OpenApiResponse(description='Patient not found or unauthorized.'),
        },
        tags=['Patients'],
        summary='Get details of a specific patient',
    )
    def get(self, request, pk):
        patient = self.get_patient(request, pk)
        serializer = PatientSerializer(patient)
        return Response(
            {
                'success': True,
                'data': serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=PatientSerializer,
        responses={
            200: PatientSerializer,
            400: OpenApiResponse(description='Validation error.'),
            404: OpenApiResponse(description='Patient not found or unauthorized.'),
        },
        tags=['Patients'],
        summary='Update patient details',
    )
    def put(self, request, pk):
        patient = self.get_patient(request, pk)
        serializer = PatientSerializer(patient, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        updated_patient = serializer.save()
        return Response(
            {
                'success': True,
                'message': 'Patient details updated successfully.',
                'data': PatientSerializer(updated_patient).data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=PatientSerializer,
        responses={
            200: PatientSerializer,
            400: OpenApiResponse(description='Validation error.'),
            404: OpenApiResponse(description='Patient not found or unauthorized.'),
        },
        tags=['Patients'],
        summary='Partially update patient details',
    )
    def patch(self, request, pk):
        patient = self.get_patient(request, pk)
        serializer = PatientSerializer(patient, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_patient = serializer.save()
        return Response(
            {
                'success': True,
                'message': 'Patient details updated successfully.',
                'data': PatientSerializer(updated_patient).data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        responses={
            200: OpenApiResponse(description='Patient record deleted successfully.'),
            404: OpenApiResponse(description='Patient not found or unauthorized.'),
        },
        tags=['Patients'],
        summary='Delete a patient record',
    )
    def delete(self, request, pk):
        patient = self.get_patient(request, pk)
        patient_name = patient.name
        patient.delete()
        return Response(
            {
                'success': True,
                'message': f'Patient record for "{patient_name}" was successfully deleted.',
            },
            status=status.HTTP_200_OK,
        )
