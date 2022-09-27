"""This module is for views creation
"""

from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import permissions, viewsets
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveDestroyAPIView,
)
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND
from WalletService.models import Transaction, Wallet
from WalletService.permissions import PostOrSafeMethodsOnly, SenderWalletOwnerPermission

from .serializers import TransactionSerializer, UserRegisterSerializer, WalletSerializer


class CreateUserView(CreateAPIView):
    """API view for registration"""

    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegisterSerializer


class ListUserView(ListAPIView):
    """API view for checking all users"""

    queryset = User.objects.all()
    permission_classes = [permissions.IsAdminUser]
    serializer_class = UserRegisterSerializer


class WalletListView(ListCreateAPIView):
    """API view for all user's wallets"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WalletSerializer

    def get_queryset(self):
        """Gets user wallets"""
        user = self.request.user
        return Wallet.objects.filter(user=user)

    def perform_create(self, serializer):
        """Transmits user data to serializer create method"""
        return serializer.save(user=self.request.user)


class WalletDetailView(RetrieveDestroyAPIView):
    """API view for a single wallet (supports get and delete)"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WalletSerializer
    lookup_field = "name"

    def get_queryset(self):
        """Gets user wallets"""
        user = self.request.user
        return Wallet.objects.filter(user=user)

    def delete(self, request, *args, **kwargs):
        """Deletes user's wallet"""
        name = kwargs["name"]
        response = super().delete(request, *args, **kwargs)
        return Response(f"Wallet {name} deleted", status=response.status_code)


class TransactionViewSet(viewsets.ModelViewSet):
    """API viewset for transactions"""

    permission_classes = [
        permissions.IsAuthenticated,
        PostOrSafeMethodsOnly,
        SenderWalletOwnerPermission,
    ]
    serializer_class = TransactionSerializer
    lookup_field = "id"

    def get_queryset(self):
        """Gets users transactions"""
        user = self.request.user
        user_wallet = user.wallet_set.all()
        user_transactions = Transaction.objects.filter(
            Q(receiver__in=user_wallet) | Q(sender__in=user_wallet)
        )
        return user_transactions


class WalletTransactionView(ListAPIView):
    """API view for listing transaction made with a particular user wallet"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        """Gets transactions of a wallet"""
        wallet_name = self.kwargs["name"]
        user = self.request.user
        user_wallets = list(user.wallet_set.all().values("name"))
        for wallet in user_wallets:
            if wallet["name"] == wallet_name:
                return Transaction.objects.filter(
                    Q(receiver__name=wallet_name) | Q(sender__name=wallet_name)
                )
        return

    def list(self, request, *args, **kwargs):
        """Lists transaction if exist. If not - 404"""
        queryset = self.get_queryset()
        if not queryset:
            return Response(
                {"Failed": "No such wallet for current user"}, status=HTTP_404_NOT_FOUND
            )
        else:
            return super().list(self, request)
