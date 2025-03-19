from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from apps.balance.models import UserBalance

Account = get_user_model()


class TestBalanceRetrieval(APITestCase):
    def setUp(self):
        self.user = Account.objects.create_user(
            email="test@example.com", password="password123"
        )
        UserBalance.objects.create(user=self.user)  # Ensure balance exists
        self.token = RefreshToken.for_user(self.user).access_token
        self.auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        self.balance_url = reverse("get_balance")

    def test_get_balance_successfully(self):
        """Test retrieving balance for an authenticated user"""

        response = self.client.get(self.balance_url, **self.auth_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["balance"], 1000)
