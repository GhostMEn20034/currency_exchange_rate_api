from django.db import transaction
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiExample
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request

from apps.balance.models import UserBalance
from .models import CurrencyExchange
from .serializers import CurrencyExchangeSerializer, CreateCurrencyExchangeRecordResponseSerializer
from .services import get_exchange_rate


class CurrencyExchangeViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Currency Exchange'],
        request={"application/json": {"type": "object", "properties": {"currency_code": {"type": "string"}}}},
        responses={
            200: CreateCurrencyExchangeRecordResponseSerializer,
            400: {
                "type": "object",
                "properties": {"detail": {"type": "string"}},
            },
        },
        examples=[
            OpenApiExample(
                name="Successfully created currency exchange record",
                description="The provided currency code is invalid or an API error occurred.",
                value={"currency_code": "USD", "rate": "41.09"},
                response_only=True,
                status_codes=[200, ]
            ),
            OpenApiExample(
                name="Invalid Currency Code",
                description="The provided currency code is invalid or an API error occurred.",
                value={"detail": "Invalid currency code or API error."},
                response_only=True,
                status_codes=[400, ]
            ),
            OpenApiExample(
                name="Insufficient Balance",
                description="The user's balance is insufficient to make the request.",
                value={"detail": "Insufficient balance."},
                response_only=True,
                status_codes=[400, ]
            ),
        ],
    )
    @action(detail=False, methods=['post'])
    def create_currency_exchange_record(self, request: Request):
        """
        Create a currency exchange record and takes 1 coin for the request
        """
        user = request.user
        currency_code = request.data.get('currency_code')

        user_balance = UserBalance.objects.get(user=user)
        if user_balance.balance <= 0:
            return Response({"detail": "Insufficient balance."}, status=status.HTTP_400_BAD_REQUEST)

        rate = get_exchange_rate(currency_code)
        if rate is None:
            return Response({"detail": "Invalid currency code or API error."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            CurrencyExchange.objects.create(user=user, currency_code=currency_code, rate=rate)
            user_balance.decrease(1)
            user_balance.save()

        return Response({"currency_code": currency_code, "rate": round(rate, 2)})
