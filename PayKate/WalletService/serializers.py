"""
WalletService serializers
"""
import random
import string

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from WalletService.models import CARDS, CURRENCIES, Wallet


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


class WalletSerializer(serializers.ModelSerializer):
    """Serializer for wallet listing and creation"""

    # overriding type and currency fields from model to specify validation in serializer,
    # as if not - serializer function validate is called AFTER model (base) field validation,
    # similar problem and explanation found here:
    # https://github.com/encode/django-rest-framework/issues/5876

    type = serializers.CharField(max_length=10)
    currency = serializers.CharField(max_length=3)

    class Meta:
        """fields config"""

        model = Wallet
        fields = (
            "name",
            "type",
            "currency",
            "balance",
            "user",
            "created_on",
            "modified_on",
        )
        read_only_fields = ("name", "balance", "user")

    def validate(self, data):
        """Serializer data valiadtion"""

        if data["type"] not in CARDS:
            raise serializers.ValidationError(
                f"{data['type']} is not a valid choice for wallet type. "
                "Please choose among {CARDS}."
            )
        if data["currency"] not in CURRENCIES:
            raise serializers.ValidationError(
                f"{data['currency']} is not a valid choice for wallet currency. "
                "Please choose among {CURRENCIES}."
            )
        return data

    def create(self, validated_data):
        """Method that creates a wallet instance:
        - checks if user can have one more wallet,
        - ctreates random name,
        - sets bonus balance according to currency
        """

        count = Wallet.objects.filter(user=validated_data["user"]).count()
        if count >= Wallet.MAX_USER_WALLETS:
            raise serializers.ValidationError(
                f"You can't have more than {Wallet.MAX_USER_WALLETS} wallets"
            )
        name = "".join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits)
            for _ in range(settings.WALLET_NAME_LENGTH)
        )

        wallet = Wallet.objects.create(
            name=name,
            **validated_data,
            balance=Wallet.get_bonus(validated_data["currency"]),
        )

        return wallet
