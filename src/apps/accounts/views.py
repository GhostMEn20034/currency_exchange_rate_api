from django.db import transaction
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.request import Request
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import UserRegistrationSerializer, UserRegistrationErrorsSerializer, TokenResponseSerializer
from apps.balance.models import UserBalance


Account = get_user_model()


@extend_schema_view(
    post=extend_schema(
        responses={
            200: {"type": "object", "properties": {"access": {"type": "string"}, "refresh": {"type": "string"}}},
            401: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
        tags=["Authentication"]
    )
)
class DocumentedTokenObtainPairView(TokenObtainPairView):
    pass


@extend_schema_view(
    post=extend_schema(
        responses={
            200: {"type": "object", "properties": {"access": {"type": "string"}, }},
            401: {"type": "object", "properties": {"detail": {"type": "string"}, "code": {"type": "string"}}},
        },
        tags=["Authentication"]
    )
)
class DocumentedTokenRefreshView(TokenRefreshView):
    pass


@extend_schema(
    request=UserRegistrationSerializer,
    responses={
        201: TokenResponseSerializer,
        400: UserRegistrationErrorsSerializer,
    },
    auth=[],
    tags=["Users"]
)
@api_view(['POST'])
@transaction.atomic
def register(request: Request):
    """
    Creates a new user and sets his initial balance to 1000 coins
    """
    serializer = UserRegistrationSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    validated_data = serializer.validated_data

    user = Account.objects.create_user(
        email=validated_data['email'],
        password=validated_data['password1'],
        first_name=validated_data['first_name'],
        last_name=validated_data['last_name'],
    )
    UserBalance.objects.create(user=user)

    refresh = RefreshToken.for_user(user)

    response_data = {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

    response_serializer = TokenResponseSerializer(response_data)

    return Response(response_serializer.data, status=status.HTTP_201_CREATED)
