"""This module is for views creation
"""
from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView
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
