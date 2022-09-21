"""
WalletService models
"""

from django.conf import settings
from django.db import models

CARDS = ["Visa", "Mastercard"]
CURRENCIES = ["USD", "EUR", "RUB"]

CARD_CHOICES = [(card, card) for card in CARDS]
CURRENCY_CHOICES = [(currency, currency) for currency in CURRENCIES]

STATUS_CHOICES = [("PAID", "PAID"), ("FAILED", "FAILED")]


class Wallet(models.Model):
    """Model that describes wallet essense"""

    MAX_USER_WALLETS = 5
    __bonus = {"USD": 3.00, "EUR": 3.00, "RUB": 100.00}
    name = models.CharField(max_length=settings.WALLET_NAME_LENGTH, unique=True)
    type = models.CharField(choices=CARD_CHOICES, max_length=10)
    currency = models.CharField(choices=CURRENCY_CHOICES, max_length=3)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        """Wallets meta"""

        ordering = ["modified_on"]

    def __str__(self) -> str:
        """Str representation of a wallet"""
        return f"Owner: {self.user}, wallet: {self.name}"

    @classmethod
    def get_bonus(cls, currency):
        """Metod that helps recognise bonus"""
        return cls.__bonus[currency]


class Transaction(models.Model):
    """Model that describes transaction essence"""

    DEFAULT_FEE = 0.10
    sender = models.ForeignKey(Wallet, related_name="sender", on_delete=models.RESTRICT)
    receiver = models.ForeignKey(
        Wallet, related_name="receiver", on_delete=models.RESTRICT
    )
    transfer_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=DEFAULT_FEE
    )
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.10)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta class"""

        ordering = ["timestamp"]

    def __str__(self) -> str:
        """Str representation of a transaction"""
        return f"id:{self.pk} - {self.sender} - {self.receiver}"
