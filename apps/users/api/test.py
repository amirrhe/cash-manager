from rest_framework.test import APITestCase
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.users.models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken


class LoginViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.username = "testuser"
        self.password = "testpassword"
        self.user = CustomUser.objects.create_user(username=self.username, password=self.password)
        self.login_url = reverse('login')

    def test_login_with_valid_credentials(self):
        data = {
            'username': self.username,
            'password': self.password,
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        self.assertIn('user_id', response.data)
        self.assertEqual(response.data['username'], self.username)

        refresh_token = response.data['refresh']
        access_token = response.data['access']
        self.assertIsNotNone(access_token)
        refresh_token_instance = RefreshToken(refresh_token)
        access_token_instance = refresh_token_instance.access_token
        self.assertEqual(access_token_instance['user_id'], self.user.id)

    def test_login_with_invalid_credentials(self):
        data = {
            'username': self.username,
            'password': 'wrongpassword',
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_login_with_missing_credentials(self):
        data = {
            'username': self.username,
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_login_with_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        data = {
            'username': self.username,
            'password': self.password,
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_login_with_non_existent_user(self):
        data = {
            'username': 'nonexistentuser',
            'password': 'password',
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)


class RegisterUserViewTestCase(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.valid_data = {
            'username': 'testuser',
            'password': 'testpassword',
            'confirm_password': 'testpassword',
        }
        self.invalid_data = {
            'username': 'testuser',
            'password': 'testpassword',
            'confirm_password': 'differentpassword',
        }

    def test_register_user_success(self):
        response = self.client.post(self.register_url, data=self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        self.assertIn('user_id', response.data)
        self.assertEqual(response.data['username'], self.valid_data['username'])
        self.assertTrue(CustomUser.objects.filter(username=self.valid_data['username']).exists())

    def test_register_user_with_invalid_data(self):
        response = self.client.post(self.register_url, data=self.invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertFalse(CustomUser.objects.filter(username=self.invalid_data['username']).exists())

    def test_register_user_with_existing_username(self):
        CustomUser.objects.create_user(username=self.valid_data['username'], password=self.valid_data['password'])
        response = self.client.post(self.register_url, data=self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
        self.assertFalse(CustomUser.objects.filter(username=self.valid_data['username']).count() > 1)

    def test_register_user_with_missing_data(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(self.register_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirm_password', response.data)
        self.assertFalse(CustomUser.objects.filter(username=self.valid_data['username']).exists())
