from django.urls import path
from .views import CurrencyExchangeViewSet


urlpatterns = [
    path(
        'currency/',
        CurrencyExchangeViewSet.as_view({'post': 'create_currency_exchange_record'}),
        name='create_currency_exchange_record',
    ),
]