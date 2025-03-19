from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter, OpenApiTypes
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request

from apps.balance.models import UserBalance
from .models import CurrencyExchange
from .serializers import (
    CurrencyExchangeSerializer,
    CreateCurrencyExchangeRecordResponseSerializer,
    CurrencyExchangeHistoryQueryParamsSerializer,
)
from .services import get_exchange_rate, apply_currency_exchange_filters
from apps.core.dataclasses import DateRange
from .pagination import CurrencyExchangePagination


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

    @extend_schema(
        tags=['Currency Exchange'],
        parameters=[
            OpenApiParameter(
                name="currency_code",
                description="Filter history by currency code (e.g., 'USD', 'EUR')",
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="start_date",
                description="Filter history by start date (format: YYYY-MM-DD)",
                required=False,
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="end_date",
                description="Filter history by end date (format: YYYY-MM-DD)",
                required=False,
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="page",
                description="Page number for pagination",
                required=False,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="page_size",
                description="Number of records per page",
                required=False,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                name="Successful Response",
                description="A paginated list of currency exchange history records.",
                value={
                    "count": 4,
                    "next": "http://localhost:8000/api/v1/history/?page=2&page_size=2",
                    "previous": None,
                    "total_pages": 2,
                    "current_page": 1,
                    "results": [
                        {
                            "user": 1,
                            "currency_code": "USD",
                            "rate": "41.00",
                            "created_at": "2024-03-18T12:00:00Z"
                        },
                        {
                            "user": 1,
                            "currency_code": "EUR",
                            "rate": "44.50",
                            "created_at": "2024-03-17T14:30:00Z"
                        }
                    ]
                },
                response_only=True,
                status_codes=["200"]
            ),
            OpenApiExample(
                name="Bad Request (Invalid Query Params)",
                description="Occurs when provided query parameters are invalid.",
                value={
                    "currency_code": ["Invalid currency code format"]
                },
                response_only=True,
                status_codes=["400"]
            ),
            OpenApiExample(
                name="Wrong Page number",
                description="Occurs when provided page number is wrong "
                            "(For example there are only 3 pages, but you specified page #10).",
                value={
                    "detail": "Invalid page."
                },
                response_only=True,
                status_codes=["400"]
            )
        ],
    )
    @action(detail=False, methods=['get'])
    def history(self, request: Request):
        user = request.user
        currency_code = request.query_params.get('currency_code')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        serializer_data = {
            "currency_code": currency_code,
        }
        if start_date and end_date:
            serializer_data["date_range"] = {
                "start_date": start_date, "end_date": end_date
            }

        serializer = CurrencyExchangeHistoryQueryParamsSerializer(data=serializer_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data

        date_range = None
        if start_date and end_date:
            date_range = DateRange(
                start_date=validated_data["date_range"]["start_date"],
                end_date=validated_data["date_range"]["end_date"]
            )

        history = CurrencyExchange.objects.filter(user=user)
        history = apply_currency_exchange_filters(history, validated_data["currency_code"], date_range)
        history = history.order_by('-created_at')

        paginator = CurrencyExchangePagination()
        paginated_history = paginator.paginate_queryset(history, request)

        return paginator.get_paginated_response(CurrencyExchangeSerializer(paginated_history, many=True).data)
