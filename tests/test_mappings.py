import pytest
from rest_framework import status
from rest_framework.test import APIClient
from apps.authentication.models import User
from apps.patients.models import Patient
from apps.doctors.models import Doctor
from apps.mappings.models import PatientDoctorMapping


@pytest.mark.django_db
class TestMappings:

    def setup_method(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email='dr.u1@hospital.test',
            name='Primary Caretaker 1',
            password='Password123!',
        )
        self.user2 = User.objects.create_user(
            email='dr.u2@hospital.test',
            name='Primary Caretaker 2',
            password='Password123!',
        )

        # Create Patient owned by user1
        self.patient1 = Patient.objects.create(
            name='Patient Alpha',
            age=45,
            gender='Male',
            contact_number='1112223333',
            created_by=self.user1,
        )

        # Create Patient owned by user2
        self.patient2 = Patient.objects.create(
            name='Patient Beta',
            age=28,
            gender='Female',
            contact_number='4445556666',
            created_by=self.user2,
        )

        # Create Doctors
        self.doctor1 = Doctor.objects.create(
            name='Dr. Stephen Strange',
            specialization='Neurosurgery',
            license_number='LIC-STRANGE-1',
            contact_number='5551230001',
            email='strange.doc@hospital.test',
        )
        self.doctor2 = Doctor.objects.create(
            name='Dr. Leonard McCoy',
            specialization='General Medicine',
            license_number='LIC-MCCOY-2',
            contact_number='5551230002',
            email='mccoy.doc@hospital.test',
        )

        self.mappings_url = '/api/mappings/'

    def test_assign_doctor_to_patient_success(self):
        self.client.force_authenticate(user=self.user1)
        payload = {
            'patient_id': self.patient1.id,
            'doctor_id': self.doctor1.id,
            'notes': 'Neurological consultation scheduled for next Monday.',
        }
        response = self.client.post(self.mappings_url, payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert response.data['data']['patient']['id'] == self.patient1.id
        assert response.data['data']['doctor']['id'] == self.doctor1.id
        assert response.data['data']['notes'] == payload['notes']

        # DB assertion
        assert PatientDoctorMapping.objects.filter(
            patient=self.patient1,
            doctor=self.doctor1,
        ).exists()

    def test_assign_doctor_to_unowned_patient_fails(self):
        # User 1 tries to assign doctor to User 2's patient
        self.client.force_authenticate(user=self.user1)
        payload = {
            'patient_id': self.patient2.id,
            'doctor_id': self.doctor1.id,
        }
        response = self.client.post(self.mappings_url, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_prevent_duplicate_doctor_assignment(self):
        # First assignment
        PatientDoctorMapping.objects.create(
            patient=self.patient1,
            doctor=self.doctor1,
            notes='First visit',
        )

        # Second attempt to assign same doctor to same patient
        self.client.force_authenticate(user=self.user1)
        payload = {
            'patient_id': self.patient1.id,
            'doctor_id': self.doctor1.id,
        }
        response = self.client.post(self.mappings_url, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_all_mappings(self):
        PatientDoctorMapping.objects.create(
            patient=self.patient1,
            doctor=self.doctor1,
        )
        PatientDoctorMapping.objects.create(
            patient=self.patient1,
            doctor=self.doctor2,
        )
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.mappings_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

    def test_get_doctors_assigned_to_specific_patient(self):
        # Assign 2 doctors to patient 1
        m1 = PatientDoctorMapping.objects.create(
            patient=self.patient1,
            doctor=self.doctor1,
            notes='Neurosurgery follow-up',
        )
        m2 = PatientDoctorMapping.objects.create(
            patient=self.patient1,
            doctor=self.doctor2,
            notes='General health check',
        )

        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/mappings/{self.patient1.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['assigned_doctors_count'] == 2
        doctor_ids = [d['doctor']['id'] for d in response.data['doctors']]
        assert self.doctor1.id in doctor_ids
        assert self.doctor2.id in doctor_ids

    def test_get_mappings_for_other_users_patient_forbidden(self):
        # User 1 tries to view mappings for User 2's patient
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/mappings/{self.patient2.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_mapping_success(self):
        mapping = PatientDoctorMapping.objects.create(
            patient=self.patient1,
            doctor=self.doctor1,
        )
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f'/api/mappings/{mapping.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert not PatientDoctorMapping.objects.filter(pk=mapping.id).exists()

    def test_delete_other_users_mapping_fails(self):
        mapping = PatientDoctorMapping.objects.create(
            patient=self.patient2,
            doctor=self.doctor1,
        )
        # User 1 tries to delete User 2's mapping
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f'/api/mappings/{mapping.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        # Confirm still in DB
        assert PatientDoctorMapping.objects.filter(pk=mapping.id).exists()
