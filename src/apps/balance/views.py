from drf_spectacular.utils import extend_schema
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from .models import UserBalance
from .serializers import UserBalanceSerializer


@extend_schema(
    responses={
        200: UserBalanceSerializer,
        401: {"type": "object", "properties": {"detail": {"type": "string"}}},
        404: {"type": "object", "properties": {"detail": {"type": "string"}}, "example": {"detail": "There's no balance for such user"}},
    },
    tags=["Balance"]
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_balance(request: Request):
    """
    Returns current user's balance
    """
    try:
        user_balance = UserBalance.objects.get(user=request.user)
    except UserBalance.DoesNotExist:
        return Response(data={"detail": "There's no balance for such user"}, status=status.HTTP_404_NOT_FOUND)

    return Response(UserBalanceSerializer(user_balance).data, status=status.HTTP_200_OK)
