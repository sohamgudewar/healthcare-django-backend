import pytest
from rest_framework import status
from rest_framework.test import APIClient
from apps.authentication.models import User
from apps.patients.models import Patient


@pytest.mark.django_db
class TestPatients:

    def setup_method(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email='doctor.user1@healthcare.test',
            name='Dr. User One',
            password='Password123!',
        )
        self.user2 = User.objects.create_user(
            email='doctor.user2@healthcare.test',
            name='Dr. User Two',
            password='Password123!',
        )
        self.patients_url = '/api/patients/'

    def test_create_patient_authenticated(self):
        self.client.force_authenticate(user=self.user1)
        payload = {
            'name': 'Eleanor Vance',
            'age': 32,
            'gender': 'Female',
            'contact_number': '+1-555-0199',
            'email': 'eleanor@example.com',
            'address': '456 Hill House Lane',
            'medical_history': 'No chronic illnesses. Mild penicillin allergy.',
        }
        response = self.client.post(self.patients_url, payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert response.data['data']['name'] == payload['name']
        assert response.data['data']['created_by'] == self.user1.id
        assert response.data['data']['created_by_email'] == self.user1.email

        # Database verification
        patient = Patient.objects.get(pk=response.data['data']['id'])
        assert patient.created_by == self.user1

    def test_create_patient_unauthenticated_fails(self):
        payload = {
            'name': 'Anonymous Patient',
            'age': 40,
            'gender': 'Male',
            'contact_number': '+1-555-0000',
        }
        response = self.client.post(self.patients_url, payload, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_patients_scoped_to_user(self):
        # Create patients for user 1
        p1 = Patient.objects.create(
            name='Patient One',
            age=25,
            gender='Male',
            contact_number='1234567890',
            created_by=self.user1,
        )
        p2 = Patient.objects.create(
            name='Patient Two',
            age=30,
            gender='Female',
            contact_number='0987654321',
            created_by=self.user1,
        )
        # Create patient for user 2
        p3 = Patient.objects.create(
            name='Patient Three (User 2)',
            age=45,
            gender='Male',
            contact_number='1122334455',
            created_by=self.user2,
        )

        # Authenticate as user 1
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.patients_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        patient_names = [p['name'] for p in response.data['data']]
        assert 'Patient One' in patient_names
        assert 'Patient Two' in patient_names
        assert 'Patient Three (User 2)' not in patient_names

    def test_get_patient_detail_success(self):
        patient = Patient.objects.create(
            name='Arthur Pendelton',
            age=62,
            gender='Male',
            contact_number='5551234567',
            created_by=self.user1,
        )
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/patients/{patient.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['name'] == 'Arthur Pendelton'

    def test_get_patient_detail_cross_user_forbidden_or_not_found(self):
        patient = Patient.objects.create(
            name='Secret Patient',
            age=50,
            gender='Female',
            contact_number='5559876543',
            created_by=self.user2,
        )
        # User 1 tries to access User 2's patient
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/patients/{patient.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_patient_details(self):
        patient = Patient.objects.create(
            name='Original Name',
            age=20,
            gender='Male',
            contact_number='5551112233',
            created_by=self.user1,
        )
        self.client.force_authenticate(user=self.user1)
        update_payload = {
            'name': 'Updated Name',
            'age': 21,
            'gender': 'Male',
            'contact_number': '5559998877',
            'address': 'New Address 101',
        }
        response = self.client.put(f'/api/patients/{patient.id}/', update_payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['name'] == 'Updated Name'
        assert response.data['data']['age'] == 21

    def test_partial_update_patient(self):
        patient = Patient.objects.create(
            name='Constant Name',
            age=40,
            gender='Female',
            contact_number='5553334444',
            created_by=self.user1,
        )
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(
            f'/api/patients/{patient.id}/',
            {'medical_history': 'Diagnosed with Type 2 Diabetes.'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['medical_history'] == 'Diagnosed with Type 2 Diabetes.'
        assert response.data['data']['name'] == 'Constant Name'

    def test_delete_patient(self):
        patient = Patient.objects.create(
            name='Patient to Delete',
            age=29,
            gender='Other',
            contact_number='5554445555',
            created_by=self.user1,
        )
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f'/api/patients/{patient.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert not Patient.objects.filter(pk=patient.id).exists()
