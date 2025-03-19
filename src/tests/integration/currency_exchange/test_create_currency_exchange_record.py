from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.currency_exchange.models import CurrencyExchange
from apps.balance.models import UserBalance

Account = get_user_model()

class CreateCurrencyExchangeRecordTests(APITestCase):
    def setUp(self):
        self.user = Account.objects.create_user(email="test@example.com", password="testpassword")
        self.user_balance = UserBalance.objects.create(user=self.user, balance=5)

        self.token = RefreshToken.for_user(self.user).access_token
        self.auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

        self.url = reverse("create_currency_exchange_record")

    @patch("apps.currency_exchange.views.get_exchange_rate")
    def test_create_currency_exchange_success(self, mock_get_exchange_rate):
        """Test successfully creating a currency exchange record with a valid currency code."""
        mock_get_exchange_rate.return_value = 41.09  # Mocked exchange rate

        response = self.client.post(self.url, {"currency_code": "USD"}, format="json", **self.auth_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["currency_code"], "USD")
        self.assertEqual(response.data["rate"], 41.09)

        self.user_balance.refresh_from_db()
        self.assertEqual(self.user_balance.balance, 4)  # Ensure balance decreased by 1

        self.assertEqual(CurrencyExchange.objects.filter(user=self.user, currency_code="USD").count(), 1)

    @patch("apps.currency_exchange.views.get_exchange_rate")
    def test_create_currency_exchange_invalid_currency(self, mock_get_exchange_rate):
        """Test failing to create a record due to an invalid currency code."""
        mock_get_exchange_rate.return_value = None  # Mock API failure

        response = self.client.post(self.url, {"currency_code": "INVALID"}, format="json", **self.auth_headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Invalid currency code or API error.")

        self.user_balance.refresh_from_db()
        self.assertEqual(self.user_balance.balance, 5)  # Balance should remain unchanged

    @patch("apps.currency_exchange.views.get_exchange_rate")
    def test_create_currency_exchange_insufficient_balance(self, mock_get_exchange_rate):
        """Test failing to create a record due to insufficient balance."""
        self.user_balance.balance = 0  # Set balance to zero
        self.user_balance.save()

        mock_get_exchange_rate.return_value = 41.09

        response = self.client.post(self.url, {"currency_code": "USD"}, format="json", **self.auth_headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Insufficient balance.")

        self.user_balance.refresh_from_db()
        self.assertEqual(self.user_balance.balance, 0)  # Balance should remain zero

        self.assertEqual(CurrencyExchange.objects.filter(user=self.user).count(), 0)

    def test_create_currency_exchange_unauthenticated(self):
        """Test request fails when user is not authenticated."""
        response = self.client.post(self.url, {"currency_code": "USD"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
