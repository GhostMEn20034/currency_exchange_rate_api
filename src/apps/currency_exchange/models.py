from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.


Account = get_user_model()


class CurrencyExchange(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    currency_code = models.CharField(max_length=10, db_index=True) # Indexed for faster filtering in request history route.
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True) # Indexed for faster filtering in request history route.

