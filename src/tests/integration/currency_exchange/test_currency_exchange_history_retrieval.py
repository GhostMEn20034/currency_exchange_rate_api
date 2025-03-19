from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime
from apps.currency_exchange.models import CurrencyExchange


Account = get_user_model()


class TestCurrencyExchangeHistoryRetrieval(APITestCase):
    def setUp(self):
        self.user1 = Account.objects.create_user(email="user1@example.com", password="password1")
        self.user2 = Account.objects.create_user(email="user2@example.com", password="password2")

        self.token = RefreshToken.for_user(self.user1).access_token
        self.auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

        self.history_url = reverse("history")

        # Bulk insert for user1
        CurrencyExchange.objects.bulk_create([
            CurrencyExchange(user=self.user1, currency_code="USD", rate=41.00, created_at=datetime(2024, 3, 18, 10, 0, 0)),
            CurrencyExchange(user=self.user1, currency_code="EUR", rate=44.50, created_at=datetime(2024, 3, 17, 15, 30, 0)),
            CurrencyExchange(user=self.user1, currency_code="GBP", rate=50.75, created_at=datetime(2024, 3, 16, 9, 15, 0)),
            CurrencyExchange(user=self.user1, currency_code="USD", rate=40.75, created_at=datetime(2024, 3, 15, 11, 45, 0)),
            CurrencyExchange(user=self.user1, currency_code="JPY", rate=150.25, created_at=datetime(2024, 3, 14, 8, 20, 0)),
            CurrencyExchange(user=self.user1, currency_code="USD", rate=41.30, created_at=datetime(2024, 3, 13, 14, 50, 0)),
            CurrencyExchange(user=self.user1, currency_code="EUR", rate=44.10, created_at=datetime(2024, 3, 12, 10, 0, 0)),
            CurrencyExchange(user=self.user1, currency_code="GBP", rate=50.00, created_at=datetime(2024, 3, 11, 17, 30, 0)),
        ])

        # Bulk insert for user2 (to test user isolation)
        CurrencyExchange.objects.bulk_create([
            CurrencyExchange(user=self.user2, currency_code="USD", rate=41.50, created_at=datetime(2024, 3, 16, 12, 0, 0)),
            CurrencyExchange(user=self.user2, currency_code="EUR", rate=44.90, created_at=datetime(2024, 3, 15, 14, 0, 0)),
        ])

    def test_users_only_see_their_own_history(self):
        """Test that users can only see their own exchange history."""
        response = self.client.get(self.history_url, format="json", **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 8)  # User 1 should only see their 8 records
        for record in response.data["results"]:
            self.assertEqual(record["user"], self.user1.id)

    def test_filter_by_currency_code(self):
        """Test filtering exchange history by currency code."""
        response = self.client.get(self.history_url, {"currency_code": "USD"}, format="json", **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)  # User 1 has 3 USD records
        for record in response.data["results"]:
            self.assertEqual(record["currency_code"], "USD")

    def test_filter_by_date_range(self):
        """Test filtering exchange history by date range, ensuring records are either on 14th or 15th day."""
        response = self.client.get(self.history_url, {"start_date": "2024-03-14", "end_date": "2024-03-15"},
                                   format="json", **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure that the records' dates are either 14th or 15th March
        for record in response.data["results"]:
            record_date = record["date"]
            record_datetime = datetime.fromisoformat(record_date)
            self.assertIn(record_datetime.day, [14, 15])

    def test_pagination_works_correctly(self):
        """Test that pagination works correctly."""
        response = self.client.get(self.history_url, {"page": 1, "page_size": 2}, format="json", **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)  # Page size is 2, so only 2 results should be returned

    def test_invalid_page_number(self):
        """Test invalid page number handling."""
        response = self.client.get(self.history_url, {"page": 10}, format="json", **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Invalid page.")

    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access the history."""
        response = self.client.get(self.history_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
