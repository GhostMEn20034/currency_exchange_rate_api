from django.contrib import admin
from .models import UserBalance

@admin.register(UserBalance)
class ModelNameAdmin(admin.ModelAdmin):
    pass
