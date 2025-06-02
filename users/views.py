from rest_framework import viewsets, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiResponse,OpenApiParameter
from .permissions import IsAdminUserOrSelfOrHasPermission
from core.mixins import MultiLookupMixin
from .filters import UserFilter
from django.contrib.auth.hashers import check_password, make_password
from .models import User
from .serializers import UserSerializer, ChangePasswordSerializer,UserRegisterSerializer,ForgotPasswordSerializer, ResetPasswordSerializer
import os
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404
from .models import User, PasswordResetToken
from datetime import timedelta

@extend_schema_view(
    list=extend_schema(
        tags=["Users"],
        summary="Retrieve a list of users",
        description="Fetch all users registered in the system.",
        parameters=[
                OpenApiParameter(
                name='all',
                type=str,
                description='If set to `true`, disables pagination and returns all rooms.',
                required=False,
                enum=['true', 'false'] 
            )]
    ),
    retrieve=extend_schema(
        tags=["Users"],
        summary="Retrieve a specific user",
        description="Fetch detailed information about a specific user by their ID.",
    ),
    create=extend_schema(
        tags=["Users"],
        summary="Create a new user",
        description="Create a new user with the required details.",
    ),
    update=extend_schema(
        tags=["Users"],
        summary="Update a user's details",
        description="Modify an existing user's information entirely (PUT method).",
    ),
    partial_update=extend_schema(
        tags=["Users"],
        summary="Partially update a user's details",
        description="Modify some fields of an existing user (PATCH method).",
    ),
    destroy=extend_schema(
        tags=["Users"],
        summary="Delete a user",
        description="Remove a user from the system by their ID.",
    ),
)
class UserViewSet(MultiLookupMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk' 

    def get_permissions(self):
        if self.action in ['register', 'login','create','forgot_password','reset_password']:
            return [AllowAny()]
        
        elif self.action in ['logout','profile','update_profile','change_password']:
            return [IsAuthenticated()]

        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return  [IsAuthenticated(), IsAdminUserOrSelfOrHasPermission()]
        
        elif self.action in ['list']:
            return [IsAuthenticated(), IsAdminUser()]

    def paginate_queryset(self, queryset):
        """
        Override paginate_queryset to check for 'all=true' query parameter.
        """
        all_param = self.request.query_params.get('all', None)
        if all_param == 'true':
            # If 'all=true', return the full queryset without pagination
            return None
        return super().paginate_queryset(queryset)

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    search_fields = ['first_name', 'last_name', 'email']

    filterset_fields = ['role']

    ordering_fields = ['first_name', 'last_name', 'email', 'created_at', 'updated_at']
    ordering = ['created_at'] 

    filterset_class = UserFilter 

    def get_serializer_class(self):
        return UserSerializer

    @extend_schema(
        summary="Register a new user",
        description="Register a new user by providing their details. Returns the created user and JWT tokens.",
        tags=["Users"],
        # serializer=UserSerializer,
        request= UserRegisterSerializer(),
        responses={
            201: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "example": "User registered successfully!"},
                        "access": {"type": "string", "example": "access_token"},
                        "refresh": {"type": "string", "example": "refresh_token"},
                        "data": {"type": "object"}
                    }
                },
                description="User successfully registered."
            ),
            400: OpenApiResponse(
                response={"type": "object", "properties": {"error": {"type": "string", "example": "Invalid data."}}},
                description="Validation error.",
            )
        }
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Custom endpoint for user registration."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'User registered successfully!',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Login a user",
        description="Authenticate a user using their email and password. Returns a pair of access and refresh tokens.",
        tags=["Users"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "example": "user@gmail.com"},
                    "password": {"type": "string", "example": "password@123"}
                },
                "required": ["email", "password"]
            }
        },
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "access": {"type": "string", "example": "access_token"},
                        "refresh": {"type": "string", "example": "refresh_token"},
                        "message": {"type": "string", "example": "Login successful."}
                    }
                },
                description="Login successful."
            ),
            401: OpenApiResponse(
                response={"type": "object", "properties": {"error": {"type": "string", "example": "Invalid credentials."}}},
                description="Invalid credentials.",
            )
        },
        examples=[
            OpenApiExample(
                "Successful Login",
                value={"email": "user@gmail.com", "password": "password@123"},
                status_codes=["200"]
            ),
            OpenApiExample(
                "Invalid Credentials",
                value={"email": "invalid_email@example.com", "password": "wrong password"},
                status_codes=["401"]
            )
        ]
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """Custom login endpoint."""
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if not user:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'message': 'Login successful.',
            'data': UserSerializer(user).data
        }, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Logout a user",
        description="Blacklist the refresh token to logout the user.",
        tags=["Users"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "refresh": {"type": "string", "example": "refresh_token"}
                },
                "required": ["refresh"]
            }
        },
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "example": "Logout successful."}
                    }
                },
                description="Logout successful."
            ),
            400: OpenApiResponse(
                response={"type": "object", "properties": {"error": {"type": "string", "example": "Invalid token."}}},
                description="Invalid token.",
            )
        }
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """Custom logout endpoint."""
        try:
            refresh_token = request.data.get('refresh')
            print(request.user)
            print(refresh_token)
            token = RefreshToken(refresh_token)
            print("token",token)
            token.blacklist()
            return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


    @extend_schema(
        summary="View Profile",
        description="Retrieve the profile details of the logged-in user.",
        tags=["Users"],
        responses={200: UserSerializer},
        )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update Profile",
        description="Update the profile details of the logged-in user.",
        tags=["Users"],
        request=UserSerializer,
        responses={200: UserSerializer},
    )
    @action(detail=False, methods=['put', 'patch'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    @extend_schema(
        summary="Change Password",
        description="Allows a logged-in user to change their password.",
        tags=["Users"],
        request=ChangePasswordSerializer,
        responses={200: {"message": "Password updated successfully."}},
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
       
        if serializer.validate_old_password(request.data.get("old_password")):
            if (request.data.get("old_password") == request.data.get("new_password")):
                return Response({"new_password": "New password must be different from the old password."}, status=status.HTTP_400_BAD_REQUEST)
            
            if serializer.is_valid():
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)

        # Format errors to return only a single message per field
        formatted_errors = {field: errors[0] for field, errors in serializer.errors.items()}
        return Response(formatted_errors, status=status.HTTP_400_BAD_REQUEST)



    @extend_schema(
        request=ForgotPasswordSerializer,
        responses={200: OpenApiResponse(description="Password reset link sent successfully.")},
        tags=["Users"]
    )
    @action(detail=False, methods=["post"], permission_classes=[AllowAny], url_path="forgot-password")
    def forgot_password(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        print(serializer,'the serializer')
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        user = User.objects.get(email=email, is_superuser=True)
        expires_at = timezone.now() + timedelta(hours=1)
        token = PasswordResetToken.objects.create(user=user, expires_at=expires_at)
        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
        reset_link = f"{frontend_url}reset-password/{token.token}"

        html_content = render_to_string('emails/password_reset_email.html', {
            'full_name': f"{user.first_name} {user.last_name}",
            'reset_link': reset_link,
            'expires_in_hours': 1,
        })

        email_msg = EmailMultiAlternatives(
            subject="Password Reset",
            body="",
            from_email=os.environ.get('EMAIL_HOST_USER'),
            to=[user.email]
        )
        email_msg.attach_alternative(html_content, "text/html")

        try:
            email_msg.send(fail_silently=False)
        except Exception as e:
            return Response({'error': f'Failed to send email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'Password reset link sent successfully.'}, status=status.HTTP_200_OK)



    @extend_schema(
        request=ResetPasswordSerializer,
        responses={200: OpenApiResponse(description="Password has been reset successfully.")},
        tags=["Users"]
    )
    @action(detail=False, methods=["post"], permission_classes=[AllowAny], url_path="reset-password")
    def reset_password(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token_uuid = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        reset_token = get_object_or_404(PasswordResetToken, token=token_uuid)
        if reset_token.is_expired():
            return Response({"error": "Token has expired"}, status=status.HTTP_400_BAD_REQUEST)

        user = reset_token.user
        user.set_password(new_password)
        user.save()

        PasswordResetToken.objects.filter(user=user).update(is_deleted=True)

        login_link = f"{os.environ.get('FRONTEND_URL', 'http://localhost:8000')}/login"
        html_content = render_to_string('emails/password_reset_successful.html', {
            'full_name': f"{user.first_name} {user.last_name}",
            'login_link': login_link,
        })

        success_email = EmailMultiAlternatives(
            subject="Password Reset Successful",
            body="",
            from_email=os.environ.get('EMAIL_HOST_USER'),
            to=[user.email]
        )
        success_email.attach_alternative(html_content, "text/html")
        try:
            success_email.send(fail_silently=False)
        except Exception as e:
            pass 

        return Response({"message": "Password has been reset successfully."})