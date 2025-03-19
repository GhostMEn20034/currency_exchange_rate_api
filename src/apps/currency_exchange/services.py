from typing import Optional

from django.conf import settings
import requests


def get_exchange_rate(currency_code: str) -> Optional[float]:
    url = f"https://v6.exchangerate-api.com/v6/{settings.EXCHANGE_RATE_API_KEY}/latest/{currency_code}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data['conversion_rates'].get("UAH")

    return None
