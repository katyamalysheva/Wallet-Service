"""This module is for views creation
"""
from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveDestroyAPIView,
)
from rest_framework.response import Response
from WalletService.models import Wallet

from .serializers import UserRegisterSerializer, WalletSerializer


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
        "Deletes user's wallet"
        name = kwargs["name"]
        response = super().delete(request, *args, **kwargs)
        return Response(f"Wallet {name} deleted", status=response.status_code)
