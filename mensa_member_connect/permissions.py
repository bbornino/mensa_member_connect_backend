from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """
    Custom permission to check if user has admin role.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')


