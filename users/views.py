from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from core.mixins import BulkOperationsMixin, MultiLookupMixin
from core.utils import generate_bulk_schema_view, generate_crud_schema_view
from core.views import BaseViewSet

from .actions import (
    change_password,
    forgot_password,
    login,
    logout,
    profile,
    register,
    resend_verification_token,
    reset_password,
    update_profile,
    verify_email,
)
from .filters import UserFilter
from .models import User
from .permissions import IsAdminUserOrSelfOrHasPermission
from .serializers import UserRegisterSerializer, UserSerializer


@generate_bulk_schema_view("User", UserSerializer)
@generate_crud_schema_view("User")
class UserViewSet(MultiLookupMixin, BulkOperationsMixin, BaseViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_class = UserFilter
    search_fields = ["first_name", "last_name", "email"]
    ordering_fields = ["first_name", "last_name", "email", "created_at", "updated_at"]
    ordering = ["created_at"]
    bulk_schema_tag = "User"

    permission_classes_by_action = {
        "register": [AllowAny],
        "login": [AllowAny],
        "forgot_password": [AllowAny],
        "reset_password": [AllowAny],
        "verify_email": [AllowAny],
        "resend_verification_token": [AllowAny],
        "logout": [IsAuthenticated],
        "profile": [IsAuthenticated],
        "update_profile": [IsAuthenticated],
        "change_password": [IsAuthenticated],
        "retrieve": [IsAuthenticated, IsAdminUserOrSelfOrHasPermission],
        "update": [IsAuthenticated, IsAdminUserOrSelfOrHasPermission],
        "partial_update": [IsAuthenticated, IsAdminUserOrSelfOrHasPermission],
        "destroy": [IsAuthenticated, IsAdminUserOrSelfOrHasPermission],
        "list": [IsAuthenticated, IsAdminUser],
        "create": [IsAuthenticated],
        "default": [IsAuthenticated],
    }

    def get_serializer_class(self):
        if self.action == "register":
            return UserRegisterSerializer
        return super().get_serializer_class()

    # ✅ Custom action assignments
    register = register
    login = login
    logout = logout
    profile = profile
    update_profile = update_profile
    change_password = change_password
    forgot_password = forgot_password
    reset_password = reset_password
    verify_email = verify_email
    resend_verification_token = resend_verification_token
