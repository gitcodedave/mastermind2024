from rest_framework.permissions import BasePermission

class IsSuperUser(BasePermission):
    """
    Custom permission - check if user is a SuperUser
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser