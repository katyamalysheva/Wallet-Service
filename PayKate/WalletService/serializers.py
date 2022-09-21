"""
WalletService serializers
"""
import decimal
import random
import string

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from WalletService.models import CARDS, CURRENCIES, Transaction, Wallet

# from django.db import transaction


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
            username=validated_data["username"], email=validated_data["email"]
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
    """Serializer for wallet listing, creation and deletion"""

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


class TransactionSerializer(serializers.ModelSerializer):
    """Serializing for transactions' listing"""

    receiver = serializers.CharField(
        source="receiver.name", max_length=settings.WALLET_NAME_LENGTH
    )
    sender = serializers.CharField(
        source="sender.name", max_length=settings.WALLET_NAME_LENGTH
    )

    class Meta:
        model = Transaction
        fields = (
            "id",
            "receiver",
            "sender",
            # "receiver_wallet",
            # "sender_wallet",
            "transfer_amount",
            "fee",
            "status",
            "timestamp",
        )
        read_only_fields = ("id", "status", "fee")

    def validate(self, data):
        receiver = get_or_none(Wallet, name=data["receiver"]["name"])
        sender = get_or_none(Wallet, name=data["sender"]["name"])

        if not receiver:
            raise serializers.ValidationError("Receiver wallet doesn't exist")
        if not sender:
            raise serializers.ValidationError("Sender wallet doesn't exist")

        # Needs to be added to permissions
        """if sender.user != self.context['request'].user:
            raise serializers.ValidationError("User don't have permission to proceed the operation")"""

        if sender.currency != receiver.currency:
            raise serializers.ValidationError("Currencies of wallets are not equal")

        if sender.user == receiver.user:
            if sender.balance < data["transfer_amount"]:
                raise serializers.ValidationError(
                    "sender wallet doesn't have enough funds for transaction"
                )
        else:
            if sender.balance < data["transfer_amount"] * decimal.Decimal(
                1.00 + Transaction.DEFAULT_FEE
            ):
                raise serializers.ValidationError(
                    "sender wallet doesn't have enough funds for transaction"
                )

        data["receiver"] = receiver
        data["sender"] = sender

        return data

    def create(self, validated_data):

        sender = validated_data["sender"]
        receiver = validated_data["receiver"]
        if sender.user == receiver.user:
            fee = 0.00
        else:
            fee = Transaction.DEFAULT_FEE

        transfer_amount_with_fee = validated_data["transfer_amount"] * decimal.Decimal(
            str(1.00 + fee)
        )
        transaction = Transaction.objects.create(
            sender=sender,
            receiver=receiver,
            fee=fee,
            transfer_amount=validated_data["transfer_amount"],
            status="FAILED",
        )
        # with transaction.atomic():
        sender.balance = sender.balance - transfer_amount_with_fee
        sender.save()
        receiver.balance = receiver.balance + validated_data["transfer_amount"]
        receiver.save()
        transaction.status = "PAID"
        return transaction


def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None
