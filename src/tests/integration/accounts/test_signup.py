from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.balance.models import UserBalance


Account = get_user_model()


class UserRegistrationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register_the_user')
        self.valid_data = {
            "email": "testuser@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password1": "securepassword123",
            "password2": "securepassword123",
        }

    def test_register_successfully(self):
        """Test that a user can be registered successfully and has an initial balance"""
        response = self.client.post(self.register_url, self.valid_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        # Check that the user is created
        user_exists = Account.objects.filter(email=self.valid_data["email"]).exists()
        self.assertTrue(user_exists)

        # Check that the UserBalance is created
        user = Account.objects.get(email=self.valid_data["email"])
        user_balance_exists = UserBalance.objects.filter(user=user).exists()
        self.assertTrue(user_balance_exists)

        # Check that the initial balance is set to 1000
        user_balance = UserBalance.objects.get(user=user)
        self.assertEqual(user_balance.balance, 1000)

    def test_register_passwords_do_not_match(self):
        """Test that registration fails when passwords do not match"""
        invalid_data = self.valid_data.copy()
        invalid_data["password2"] = "differentpassword"

        response = self.client.post(self.register_url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn("non_field_errors", response.data)

    def test_register_duplicate_email_fails(self):
        """Test that registration fails if email already exists"""
        Account.objects.create_user(email=self.valid_data["email"], password="testpass123")

        response = self.client.post(self.register_url, self.valid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn("email", response.data)

    def test_register_missing_required_fields(self):
        """Test that registration fails if required fields are missing"""
        response = self.client.post(self.register_url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn("email", response.data)
        self.assertIn("first_name", response.data)
        self.assertIn("password1", response.data)
        self.assertIn("password2", response.data)
