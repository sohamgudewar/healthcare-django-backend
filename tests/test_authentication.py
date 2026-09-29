import pytest
from rest_framework import status
from rest_framework.test import APIClient
from apps.authentication.models import User


@pytest.mark.django_db
class TestAuthentication:

    def setup_method(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.profile_url = '/api/auth/me/'

    def test_register_user_success(self):
        payload = {
            'name': 'Dr. Alice Morgan',
            'email': 'alice.morgan@healthcare.test',
            'password': 'SecurePassword123!',
        }
        response = self.client.post(self.register_url, payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert response.data['data']['user']['email'] == payload['email'].lower()
        assert response.data['data']['user']['name'] == payload['name']
        assert 'tokens' in response.data['data']
        assert 'access' in response.data['data']['tokens']

        # Verify persisted in database
        assert User.objects.filter(email='alice.morgan@healthcare.test').exists()

    def test_register_duplicate_email_fails(self):
        User.objects.create_user(
            email='duplicate@healthcare.test',
            name='First User',
            password='password123',
        )
        payload = {
            'name': 'Second User',
            'email': 'duplicate@healthcare.test',
            'password': 'password123',
        }
        response = self.client.post(self.register_url, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False

    def test_register_short_password_fails(self):
        payload = {
            'name': 'Bob Tester',
            'email': 'bob@healthcare.test',
            'password': '123',  # Less than min 6 chars
        }
        response = self.client.post(self.register_url, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_blank_name_fails(self):
        payload = {
            'name': '   ',
            'email': 'blank@healthcare.test',
            'password': 'password123',
        }
        response = self.client.post(self.register_url, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_success(self):
        user = User.objects.create_user(
            email='login.test@healthcare.test',
            name='Login User',
            password='SecretPassword123',
        )
        payload = {
            'email': 'login.test@healthcare.test',
            'password': 'SecretPassword123',
        }
        response = self.client.post(self.login_url, payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'access' in response.data['data']['tokens']
        assert 'refresh' in response.data['data']['tokens']
        assert response.data['data']['user']['email'] == user.email

    def test_login_case_insensitive_email(self):
        User.objects.create_user(
            email='case.test@healthcare.test',
            name='Case User',
            password='SecretPassword123',
        )
        payload = {
            'email': 'CASE.TEST@HEALTHCARE.TEST',
            'password': 'SecretPassword123',
        }
        response = self.client.post(self.login_url, payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True

    def test_login_invalid_password(self):
        User.objects.create_user(
            email='invalid.pass@healthcare.test',
            name='User',
            password='CorrectPassword123',
        )
        payload = {
            'email': 'invalid.pass@healthcare.test',
            'password': 'WrongPassword!',
        }
        response = self.client.post(self.login_url, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False

    def test_login_nonexistent_user(self):
        payload = {
            'email': 'nonexistent@healthcare.test',
            'password': 'SomePassword123',
        }
        response = self.client.post(self.login_url, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_authenticated_profile_access(self):
        user = User.objects.create_user(
            email='profile@healthcare.test',
            name='Profile User',
            password='Password123',
        )
        self.client.force_authenticate(user=user)
        response = self.client.get(self.profile_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['email'] == user.email

    def test_unauthenticated_profile_access_denied(self):
        response = self.client.get(self.profile_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
