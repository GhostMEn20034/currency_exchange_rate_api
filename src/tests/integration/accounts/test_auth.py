from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


Account = get_user_model()


class TestJWTAuth(APITestCase):
    def setUp(self):
        """Create a test user with an email field"""
        self.user = Account.objects.create_user(email='testuser@example.com', password='testpassword')

        self.token_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')

    def test_token_obtain_success(self):
        """Test obtaining token with valid email credentials"""
        response = self.client.post(self.token_url, {'email': 'testuser@example.com', 'password': 'testpassword'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_token_obtain_failure(self):
        """Test obtaining token with invalid credentials"""
        response = self.client.post(self.token_url, {'email': 'testuser@example.com', 'password': 'wrongpassword'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

    def test_refresh_token_success(self):
        """Test refreshing token with a valid refresh token"""
        response = self.client.post(self.token_url, {'email': 'testuser@example.com', 'password': 'testpassword'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        refresh_token = response.data['refresh']

        response = self.client.post(self.refresh_url, {'refresh': refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_refresh_token_failure(self):
        """Test refreshing token with an invalid token"""
        response = self.client.post(self.refresh_url, {'refresh': 'invalid_refresh_token'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

