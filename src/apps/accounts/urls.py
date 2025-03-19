from django.urls import path, include
from .views import register, DocumentedTokenRefreshView, DocumentedTokenObtainPairView

urlpatterns = [
    path('auth/', include([
        path('token/', DocumentedTokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', DocumentedTokenRefreshView.as_view(), name='token_refresh'),
    ])),
    path('register/', register, name='register_the_user'),
]