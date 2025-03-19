from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator


Account = get_user_model()


class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=Account.objects.all())]
    )
    first_name = serializers.CharField(min_length=1, max_length=50, required=True)
    last_name = serializers.CharField(max_length=50, allow_blank=True)

    password1 = serializers.CharField(
        write_only=True, style={'input_type': 'password'}, min_length=8,
    )
    password2 = serializers.CharField(
        write_only=True, style={'input_type': 'password'}, min_length=8,
    )

    def validate(self, data):
        """
        Check that password1 and password2 match.
        """
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords must match.")
        return data


class UserRegistrationErrorsSerializer(serializers.Serializer):
    """Only for swagger ui"""
    email = serializers.ListField(child=serializers.CharField(), required=False)
    first_name = serializers.ListField(child=serializers.CharField(), required=False)
    last_name = serializers.ListField(child=serializers.CharField(), required=False)
    password1 = serializers.ListField(child=serializers.CharField(), required=False)
    password2 = serializers.ListField(child=serializers.CharField(), required=False)
    non_field_errors = serializers.ListField(child=serializers.CharField(), required=False)


class TokenResponseSerializer(serializers.Serializer):
    """Serializer for JWT token response."""
    refresh = serializers.CharField()
    access = serializers.CharField()
