"""WalletService custom permissions
"""
from rest_framework import permissions
from rest_framework.exceptions import MethodNotAllowed, NotFound
from WalletService.models import Wallet
from WalletService.serializers import get_object_if_exists


class PostOrSafeMethodsOnly(permissions.BasePermission):
    """Permission for blocking all methods besides safe and post"""

    def has_permission(self, request, view):
        """Checks permissins for all request types"""
        if request.method in permissions.SAFE_METHODS or request.method == "POST":
            return True
        else:
            raise MethodNotAllowed(request.method)


class SenderWalletOwnerPermission(permissions.BasePermission):
    """Permission for prceeding transactions
    If sender wallet owner not a current user - transaction can't be made
    """

    message = "Current user have no rights to proceed the transaction:"
    "sender wallet is not user's wallet"

    def has_permission(self, request, view):
        """Checks permissins for all request types"""
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            wallet = get_object_if_exists(Wallet, name=request.data.get("sender"))
            if wallet:
                return wallet.user == request.user
            else:
                raise NotFound(detail="Sender wallet doesn't exist", code=404)
