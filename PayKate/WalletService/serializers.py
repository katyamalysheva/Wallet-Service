"""
WalletService serializers
"""
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""

    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "password", "password2", "email"]
        write_only_fields = ["password", "password2"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        """Creating user and hashing password"""
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

    def validate(self, attrs):
        """Extended validation"""

        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError("Passwords don't match!")
        validate_password(attrs["password"])
        attrs.pop("password2")
        return super().validate(attrs)
