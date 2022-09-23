"""Models registered in admin"""
from django.contrib import admin
from WalletService.models import Transaction, Wallet

# Register your models here.
admin.site.register(Wallet)
admin.site.register(Transaction)
