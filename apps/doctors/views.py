from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from .models import Doctor
from .serializers import DoctorSerializer


class DoctorListCreateView(APIView):
    """
    List all doctors or create a new doctor entry in the healthcare directory.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='search',
                description='Search by doctor name or specialization',
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name='specialization',
                description='Filter by doctor specialization',
                required=False,
                type=str,
            ),
        ],
        responses={200: DoctorSerializer(many=True)},
        tags=['Doctors'],
        summary='Retrieve all registered doctors',
    )
    def get(self, request):
        queryset = Doctor.objects.all()

        search_query = request.query_params.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | Q(specialization__icontains=search_query)
            )

        specialization = request.query_params.get('specialization', '').strip()
        if specialization:
            queryset = queryset.filter(specialization__iexact=specialization)

        serializer = DoctorSerializer(queryset, many=True)
        return Response(
            {
                'success': True,
                'count': queryset.count(),
                'data': serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=DoctorSerializer,
        responses={
            201: OpenApiResponse(description='Doctor created successfully.', response=DoctorSerializer),
            400: OpenApiResponse(description='Validation error or duplicate license/email.'),
        },
        tags=['Doctors'],
        summary='Add a new doctor to the directory',
    )
    def post(self, request):
        serializer = DoctorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        doctor = serializer.save()
        return Response(
            {
                'success': True,
                'message': 'Doctor profile created successfully.',
                'data': DoctorSerializer(doctor).data,
            },
            status=status.HTTP_201_CREATED,
        )


class DoctorDetailView(APIView):
    """
    Retrieve, update, or delete a specific doctor profile.
    """
    permission_classes = [IsAuthenticated]

    def get_doctor(self, pk):
        return get_object_or_404(Doctor, pk=pk)

    @extend_schema(
        responses={
            200: DoctorSerializer,
            404: OpenApiResponse(description='Doctor not found.'),
        },
        tags=['Doctors'],
        summary='Get details of a specific doctor',
    )
    def get(self, request, pk):
        doctor = self.get_doctor(pk)
        serializer = DoctorSerializer(doctor)
        return Response(
            {
                'success': True,
                'data': serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=DoctorSerializer,
        responses={
            200: DoctorSerializer,
            400: OpenApiResponse(description='Validation error.'),
            404: OpenApiResponse(description='Doctor not found.'),
        },
        tags=['Doctors'],
        summary='Update doctor details',
    )
    def put(self, request, pk):
        doctor = self.get_doctor(pk)
        serializer = DoctorSerializer(doctor, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        updated_doctor = serializer.save()
        return Response(
            {
                'success': True,
                'message': 'Doctor details updated successfully.',
                'data': DoctorSerializer(updated_doctor).data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=DoctorSerializer,
        responses={
            200: DoctorSerializer,
            400: OpenApiResponse(description='Validation error.'),
            404: OpenApiResponse(description='Doctor not found.'),
        },
        tags=['Doctors'],
        summary='Partially update doctor details',
    )
    def patch(self, request, pk):
        doctor = self.get_doctor(pk)
        serializer = DoctorSerializer(doctor, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_doctor = serializer.save()
        return Response(
            {
                'success': True,
                'message': 'Doctor details updated successfully.',
                'data': DoctorSerializer(updated_doctor).data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        responses={
            200: OpenApiResponse(description='Doctor record deleted successfully.'),
            404: OpenApiResponse(description='Doctor not found.'),
        },
        tags=['Doctors'],
        summary='Delete a doctor record',
    )
    def delete(self, request, pk):
        doctor = self.get_doctor(pk)
        doctor_name = doctor.name
        doctor.delete()
        return Response(
            {
                'success': True,
                'message': f'Doctor profile for "{doctor_name}" was successfully deleted.',
            },
            status=status.HTTP_200_OK,
        )
