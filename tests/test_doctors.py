import pytest
from rest_framework import status
from rest_framework.test import APIClient
from apps.authentication.models import User
from apps.doctors.models import Doctor


@pytest.mark.django_db
class TestDoctors:

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='admin.doctor@healthcare.test',
            name='Hospital Admin',
            password='AdminPassword123!',
        )
        self.doctors_url = '/api/doctors/'

    def test_create_doctor_authenticated(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            'name': 'Dr. Meredith Grey',
            'specialization': 'General Surgery',
            'license_number': 'MD-998822',
            'contact_number': '+1-555-888-9999',
            'email': 'meredith.grey@greysloan.test',
            'years_of_experience': 12,
            'hospital_affiliation': 'Grey Sloan Memorial Hospital',
        }
        response = self.client.post(self.doctors_url, payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert response.data['data']['name'] == payload['name']
        assert response.data['data']['license_number'] == 'MD-998822'

        # Verify DB record
        assert Doctor.objects.filter(license_number='MD-998822').exists()

    def test_create_doctor_unauthenticated_fails(self):
        payload = {
            'name': 'Dr. House',
            'specialization': 'Diagnostics',
            'license_number': 'MD-000001',
            'contact_number': '555-123-4567',
            'email': 'house@ppth.test',
        }
        response = self.client.post(self.doctors_url, payload, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_doctor_duplicate_license_fails(self):
        Doctor.objects.create(
            name='First Doctor',
            specialization='Cardiology',
            license_number='LIC-112233',
            contact_number='1112223333',
            email='first@hospital.test',
        )
        self.client.force_authenticate(user=self.user)
        payload = {
            'name': 'Second Doctor',
            'specialization': 'Neurology',
            'license_number': 'LIC-112233',  # Duplicate
            'contact_number': '4445556666',
            'email': 'second@hospital.test',
        }
        response = self.client.post(self.doctors_url, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_doctor_duplicate_email_fails(self):
        Doctor.objects.create(
            name='Doctor A',
            specialization='Dermatology',
            license_number='LIC-A',
            contact_number='1111111111',
            email='same.email@hospital.test',
        )
        self.client.force_authenticate(user=self.user)
        payload = {
            'name': 'Doctor B',
            'specialization': 'Pediatrics',
            'license_number': 'LIC-B',
            'contact_number': '2222222222',
            'email': 'SAME.EMAIL@HOSPITAL.TEST',  # Duplicate case-insensitive
        }
        response = self.client.post(self.doctors_url, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_all_doctors(self):
        Doctor.objects.create(
            name='Dr. Strange',
            specialization='Neurosurgery',
            license_number='LIC-STRANGE',
            contact_number='1234567890',
            email='strange@marvel.test',
        )
        Doctor.objects.create(
            name='Dr. Watson',
            specialization='General Medicine',
            license_number='LIC-WATSON',
            contact_number='0987654321',
            email='watson@baker.test',
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.doctors_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 2

    def test_search_and_filter_doctors(self):
        Doctor.objects.create(
            name='Dr. Gregory House',
            specialization='Diagnostic Medicine',
            license_number='LIC-HOUSE',
            contact_number='5550001111',
            email='house.diag@test.com',
        )
        Doctor.objects.create(
            name='Dr. Lisa Cuddy',
            specialization='Endocrinology',
            license_number='LIC-CUDDY',
            contact_number='5550002222',
            email='cuddy.endo@test.com',
        )
        self.client.force_authenticate(user=self.user)

        # Search by name
        res = self.client.get('/api/doctors/?search=House')
        assert res.status_code == status.HTTP_200_OK
        assert res.data['count'] == 1
        assert res.data['data'][0]['name'] == 'Dr. Gregory House'

        # Filter by specialization
        res_spec = self.client.get('/api/doctors/?specialization=Endocrinology')
        assert res_spec.status_code == status.HTTP_200_OK
        assert res_spec.data['count'] == 1
        assert res_spec.data['data'][0]['name'] == 'Dr. Lisa Cuddy'

    def test_get_doctor_detail(self):
        doc = Doctor.objects.create(
            name='Dr. Shaun Murphy',
            specialization='Pediatric Surgery',
            license_number='LIC-MURPHY',
            contact_number='5559990000',
            email='murphy@stbonaventure.test',
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/doctors/{doc.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['name'] == 'Dr. Shaun Murphy'

    def test_update_doctor(self):
        doc = Doctor.objects.create(
            name='Dr. John Dorian',
            specialization='Internal Medicine',
            license_number='LIC-JD',
            contact_number='5557778888',
            email='jd@sacredheart.test',
            years_of_experience=3,
        )
        self.client.force_authenticate(user=self.user)
        update_payload = {
            'name': 'Dr. John Dorian, Chief of Medicine',
            'specialization': 'Internal Medicine',
            'license_number': 'LIC-JD',
            'contact_number': '5557778888',
            'email': 'jd@sacredheart.test',
            'years_of_experience': 10,
        }
        response = self.client.put(f'/api/doctors/{doc.id}/', update_payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['years_of_experience'] == 10

    def test_delete_doctor(self):
        doc = Doctor.objects.create(
            name='Temporary Doctor',
            specialization='Radiology',
            license_number='LIC-TEMP',
            contact_number='5550009999',
            email='temp@hospital.test',
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/doctors/{doc.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert not Doctor.objects.filter(pk=doc.id).exists()
