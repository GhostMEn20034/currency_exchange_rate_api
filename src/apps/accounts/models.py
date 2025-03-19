from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import AccountManager


class Account(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True)

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ['first_name', 'last_name', ]

    objects = AccountManager()

    def __str__(self):
        return self.email
