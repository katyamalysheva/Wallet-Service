"""This module is for views creation
"""
from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework.generics import CreateAPIView, ListAPIView

from .serializers import UserRegisterSerializer


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
