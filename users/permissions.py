from rest_framework.permissions import BasePermission


class IsAdminUserOrSelfOrHasPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        # Check if the user is the same as the object's user (self-check)
        if request.user.is_superuser or request.user.is_staff:
            return True

        if obj == request.user:
            return True

        return False
