"""
WalletService models:

Wallet:
- id
- name - unique random 8 symbols of latin alphabet and digits. Example: MO72RTX3
- type - 2 possible choices: Visa or Mastercard
- currency - 3 possible choices: USD, EUR, RUB
- balance - balance rounding up to 2 decimal places. Example: 1.38 - ok,1.377 - wrong
- user - user_id, who created the wallet(FK User)
- created_on - datetime, when wallet was created
- modified_on - datetime, when wallet was modified

User can't create more than 5 wallets.
"""

from django.conf import settings
from django.db import models

CARDS = ["Visa", "Mastercard"]
CURRENCIES = ["USD", "EUR", "RUB"]

CARD_CHOICES = [(card, card) for card in CARDS]
CURRENCY_CHOICES = [(currency, currency) for currency in CURRENCIES]


class Wallet(models.Model):
    "Model that describes wallet essense"
    __max_user_wallets = 5
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
    def max_user_wallets(cls):
        """Method that helps getting maximum value of wallets that user can have"""
        return cls.__max_user_wallets

    @classmethod
    def get_bonus(cls, currency):
        """Metod that helps recognise bonus"""
        return cls.__bonus[currency]
