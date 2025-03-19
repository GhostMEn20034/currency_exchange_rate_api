from datetime import datetime, time
from typing import Optional
import requests
from django.conf import settings
from django.db.models import QuerySet

from .models import CurrencyExchange
from apps.core.dataclasses import DateRange


def get_exchange_rate(currency_code: str) -> Optional[float]:
    url = f"https://v6.exchangerate-api.com/v6/{settings.EXCHANGE_RATE_API_KEY}/latest/{currency_code}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data['conversion_rates'].get("UAH")

    return None

def apply_currency_exchange_filters(
        queryset: QuerySet[CurrencyExchange],
        currency_code: Optional[str] = None,
        date_range: Optional[DateRange] = None,
) -> QuerySet[CurrencyExchange]:
    if currency_code:
        queryset = queryset.filter(currency_code=currency_code)

    if date_range:
        start_datetime = datetime.combine(date_range.start_date, time.min)  # 00:00:00
        end_datetime = datetime.combine(date_range.end_date, time.max)  # 23:59:59.999999

        queryset = queryset.filter(created_at__range=[start_datetime, end_datetime])

    return queryset
