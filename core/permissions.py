from rest_framework.permissions import BasePermission,IsAdminUser
from guardian.shortcuts import get_objects_for_user

class IsAdminUserOrSelfOrHasPermission(BasePermission):
  
  
    def has_object_permission(self, request, view, obj):
        # Check if the staff is the same as the object's staff (self-check)
        if(request.user.is_superuser or request.user.is_staff):
            return True
        if obj.id == request.user.id:
            return True
        return False



class IsStaffOrAdmin(BasePermission):
    """
    Allows access only to the cleaner who owns the shift or an admin.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True  # Admins can manage all shifts
        return obj.cleaner or obj.supervisor == request.user  # Staffs can manage their own shifts

