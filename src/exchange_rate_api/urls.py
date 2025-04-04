from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include([
        path('', include('apps.accounts.urls')),
        path('', include('apps.balance.urls')),
        path('', include('apps.currency_exchange.urls')),
    ])),
]

# Interactive docs enabled only if the app is in Debug Mode
if settings.DEBUG:
    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    ]
