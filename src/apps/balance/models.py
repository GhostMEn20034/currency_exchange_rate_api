from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import F


Account = get_user_model()


class UserBalance(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    balance = models.PositiveIntegerField(default=1000)

    def decrease(self, amount: int) -> None:
        """
        Decreases the balance by the given amount.
        """
        # F object used to avoid race conditions
        # See:
        # https://docs.djangoproject.com/en/5.1/ref/models/expressions/#avoiding-race-conditions-using-f
        self.balance = F('balance') - amount


    def __str__(self):
        return f"{self.user.first_name}'s balance"
