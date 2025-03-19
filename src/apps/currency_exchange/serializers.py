from decimal import Decimal

from rest_framework import serializers

from .models import CurrencyExchange


class CurrencyExchangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyExchange
        fields = '__all__'


class CreateCurrencyExchangeRecordResponseSerializer(serializers.Serializer):
    """
    For swagger ui only
    """
    currency_code = serializers.CharField(max_length=10)
    rate = serializers.DecimalField(max_digits=10, decimal_places=2)

