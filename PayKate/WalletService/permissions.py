from rest_framework import permissions


class SenderWalletOwnerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        print(request.data)
        return False
