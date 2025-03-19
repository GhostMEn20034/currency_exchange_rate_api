from django.contrib import admin

from .models import CurrencyExchange

@admin.register(CurrencyExchange)
class ModelNameAdmin(admin.ModelAdmin):
    list_filter = ('created_at', 'currency_code')
    list_display = ('__str__', 'currency_code', 'rate', 'user', )

    def get_queryset(self, request):
        """
        Overrides the default queryset to customize the objects displayed.
        """
        qs = super().get_queryset(request)
        qs = qs.select_related('user')
        return qs