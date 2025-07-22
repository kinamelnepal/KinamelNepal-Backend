import os
import random
import uuid
from datetime import timedelta

from django.contrib.auth import authenticate
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import EmailVerificationToken, PasswordResetToken, User
from .serializers import (
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResendTokenSerializer,
    ResetPasswordSerializer,
    UserRegisterSerializer,
    UserSerializer,
    VerifyEmailSerializer,
)

EMAIL_CONTENT_TYPE = "text/html"
VERIFY_EMAIL_TEMPLATE = "emails/verify_email.html"


@extend_schema(
    summary="Register a new user",
    description="Register a new user by providing their details. Returns the created user and JWT tokens.",
    tags=["User"],
    request=UserRegisterSerializer(),
    responses={
        201: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "User registered successfully!",
                    },
                    "access": {"type": "string", "example": "access_token"},
                    "refresh": {"type": "string", "example": "refresh_token"},
                    "data": {"type": "object"},
                },
            },
            description="User successfully registered.",
        ),
        400: OpenApiResponse(
            response={
                "type": "object",
                "properties": {"error": {"type": "string", "example": "Invalid data."}},
            },
            description="Validation error.",
        ),
    },
)
@action(detail=False, methods=["post"], permission_classes=[AllowAny])
def register(self, request):
    """Custom endpoint for user registration and email verification."""
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    user.is_active = False
    user.save()
    token = EmailVerificationToken.objects.create(user=user)
    verify_link = f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/verify-email?token={token.token}"
    html_content = render_to_string(
        VERIFY_EMAIL_TEMPLATE,
        {
            "full_name": f"{user.first_name} {user.last_name}",
            "verify_link": verify_link,
        },
    )

    verification_email = EmailMultiAlternatives(
        subject="Verify Your Email Address",
        body="",
        from_email=os.environ.get("EMAIL_HOST_USER"),
        to=[user.email],
    )
    verification_email.attach_alternative(html_content, EMAIL_CONTENT_TYPE)
    try:
        verification_email.send(fail_silently=False)
    except Exception:
        pass

    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "message": "User registered successfully! Please check your email to verify your account.",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "data": serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


@extend_schema(
    summary="Login a user",
    description="Authenticate a user using their email and password. Returns a pair of access and refresh tokens.",
    tags=["User"],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "example": "user@gmail.com"},
                "password": {"type": "string", "example": "password@123"},
            },
            "required": ["email", "password"],
        }
    },
    responses={
        200: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "access": {"type": "string", "example": "access_token"},
                    "refresh": {"type": "string", "example": "refresh_token"},
                    "message": {"type": "string", "example": "Login successful."},
                },
            },
            description="Login successful.",
        ),
        401: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "Invalid credentials."}
                },
            },
            description="Invalid credentials.",
        ),
    },
    examples=[
        OpenApiExample(
            "Successful Login",
            value={"email": "user@gmail.com", "password": "password@123"},
            status_codes=["200"],
        ),
        OpenApiExample(
            "Invalid Credentials",
            value={
                "email": "invalid_email@example.com",
                "password": "wrong password",
            },
            status_codes=["401"],
        ),
    ],
)
@action(detail=False, methods=["post"], permission_classes=[AllowAny])
def login(self, request):
    """Custom login endpoint."""
    email = request.data.get("email")
    password = request.data.get("password")
    user = authenticate(request, email=email, password=password)

    if not user:
        return Response(
            {"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.email_verified:
        return Response(
            {"error": "Please verify your email address before logging in."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "message": "Login successful.",
            "data": UserSerializer(user).data,
        },
        status=status.HTTP_200_OK,
    )


@extend_schema(
    summary="Logout a user",
    description="Blacklist the refresh token to logout the user.",
    tags=["User"],
    request={
        "application/json": {
            "type": "object",
            "properties": {"refresh": {"type": "string", "example": "refresh_token"}},
            "required": ["refresh"],
        }
    },
    responses={
        200: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "Logout successful."}
                },
            },
            description="Logout successful.",
        ),
        400: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "Invalid token."}
                },
            },
            description="Invalid token.",
        ),
    },
)
@action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
def logout(self, request):
    """Custom logout endpoint."""
    try:
        refresh_token = request.data.get("refresh")
        print(request.user)
        print(refresh_token)
        token = RefreshToken(refresh_token)
        print("token", token)
        token.blacklist()
        return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)
    except Exception:
        return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="View Profile",
    description="Retrieve the profile details of the logged-in user.",
    tags=["User"],
    responses={200: UserSerializer},
)
@action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
def profile(self, request):
    user = request.user
    serializer = self.get_serializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Update Profile",
    description="Update the profile details of the logged-in user.",
    tags=["User"],
    request=UserSerializer,
    responses={200: UserSerializer},
)
@action(detail=False, methods=["put", "patch"], permission_classes=[IsAuthenticated])
def update_profile(self, request):
    user = request.user
    serializer = self.get_serializer(user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Change Password",
    description="Allows a logged-in user to change their password.",
    tags=["User"],
    request=ChangePasswordSerializer,
    responses={200: {"message": "Password updated successfully."}},
)
@action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
def change_password(self, request):
    user = request.user
    serializer = ChangePasswordSerializer(
        data=request.data, context={"request": request}
    )

    if serializer.validate_old_password(request.data.get("old_password")):
        if request.data.get("old_password") == request.data.get("new_password"):
            return Response(
                {
                    "new_password": "New password must be different from the old password."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if serializer.is_valid():
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response(
                {"message": "Password updated successfully."},
                status=status.HTTP_200_OK,
            )

    # Format errors to return only a single message per field
    formatted_errors = {field: errors[0] for field, errors in serializer.errors.items()}
    return Response(formatted_errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=ForgotPasswordSerializer,
    responses={
        200: OpenApiResponse(description="Password reset link sent successfully.")
    },
    tags=["User"],
)
@action(
    detail=False,
    methods=["post"],
    permission_classes=[AllowAny],
    url_path="forgot-password",
)
def forgot_password(self, request):
    serializer = ForgotPasswordSerializer(data=request.data)
    print(serializer, "the serializer")
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data["email"]
    user = User.objects.get(email=email)
    expires_at = timezone.now() + timedelta(hours=1)
    token = PasswordResetToken.objects.create(user=user, expires_at=expires_at)
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    reset_link = f"{frontend_url}/reset-password/{token.token}"

    html_content = render_to_string(
        "emails/password_reset_email.html",
        {
            "full_name": f"{user.first_name} {user.last_name}",
            "reset_link": reset_link,
            "expires_in_hours": 1,
        },
    )

    email_msg = EmailMultiAlternatives(
        subject="Password Reset",
        body="",
        from_email=os.environ.get("EMAIL_HOST_USER"),
        to=[user.email],
    )
    email_msg.attach_alternative(html_content, EMAIL_CONTENT_TYPE)

    try:
        email_msg.send(fail_silently=False)
    except Exception as e:
        return Response(
            {"error": f"Failed to send email: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {"message": "Password reset link sent successfully."},
        status=status.HTTP_200_OK,
    )


@extend_schema(
    request=ResetPasswordSerializer,
    responses={
        200: OpenApiResponse(description="Password has been reset successfully.")
    },
    tags=["User"],
)
@action(
    detail=False,
    methods=["post"],
    permission_classes=[AllowAny],
    url_path="reset-password",
)
def reset_password(self, request):
    serializer = ResetPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    token_uuid = serializer.validated_data["token"]
    new_password = serializer.validated_data["new_password"]

    reset_token = get_object_or_404(PasswordResetToken, token=token_uuid)
    if reset_token.is_expired():
        return Response(
            {"error": "Token has expired"}, status=status.HTTP_400_BAD_REQUEST
        )

    user = reset_token.user
    user.set_password(new_password)
    user.save()

    PasswordResetToken.objects.filter(user=user).update(is_deleted=True)

    login_link = f"{os.environ.get('FRONTEND_URL', 'http://localhost:8000')}/login"
    html_content = render_to_string(
        "emails/password_reset_successful.html",
        {
            "full_name": f"{user.first_name} {user.last_name}",
            "login_link": login_link,
        },
    )

    success_email = EmailMultiAlternatives(
        subject="Password Reset Successful",
        body="",
        from_email=os.environ.get("EMAIL_HOST_USER"),
        to=[user.email],
    )
    success_email.attach_alternative(html_content, EMAIL_CONTENT_TYPE)
    try:
        success_email.send(fail_silently=False)
    except Exception:
        pass

    return Response({"message": "Password has been reset successfully."})


@extend_schema(
    request=VerifyEmailSerializer,
    responses={
        200: OpenApiResponse(description="Email has been verified successfully.")
    },
    tags=["User"],
)
@action(
    detail=False,
    methods=["post"],
    permission_classes=[AllowAny],
    url_path="verify-email",
)
def verify_email(self, request):
    serializer = VerifyEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    token_uuid = serializer.validated_data["token"]

    token = get_object_or_404(EmailVerificationToken, token=token_uuid)

    if token.is_expired():
        return Response(
            {"error": "Token has expired."}, status=status.HTTP_400_BAD_REQUEST
        )

    user = token.user
    user.is_active = True
    user.email_verified = True
    user.save()

    EmailVerificationToken.objects.filter(user=user).update(is_deleted=True)

    html_content = render_to_string(
        "emails/email_verified_successful.html",
        {
            "full_name": f"{user.first_name} {user.last_name}",
            "login_link": f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/login",
        },
    )

    success_email = EmailMultiAlternatives(
        subject="Email Verified Successfully",
        body="",
        from_email=os.environ.get("EMAIL_HOST_USER"),
        to=[user.email],
    )
    success_email.attach_alternative(html_content, EMAIL_CONTENT_TYPE)
    try:
        success_email.send(fail_silently=False)
    except Exception:
        pass

    return Response(
        {"message": "Email has been verified successfully."},
        status=status.HTTP_200_OK,
    )


@extend_schema(
    summary="Resend OTP/Token for email verification",
    description="Resend the OTP/Token to the user’s email if the user is not verified.",
    tags=["User"],
    request=ResendTokenSerializer,
    responses={
        200: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "OTP/Token resent successfully.",
                    }
                },
            },
            description="OTP/Token sent successfully.",
        ),
        400: OpenApiResponse(
            response={
                "type": "object",
                "properties": {"error": {"type": "string"}},
            },
            description="Validation or logic error.",
        ),
    },
)
@action(
    detail=False,
    methods=["post"],
    permission_classes=[AllowAny],
    serializer_class=ResendTokenSerializer,
    url_path="resend-verification-token",
    parser_classes=[JSONParser],
)
def resend_verification_token(self, request):
    serializer = ResendTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data["email"]
    is_mobile = serializer.validated_data["is_mobile"]
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found."}, status=status.HTTP_400_BAD_REQUEST
        )

    if user.email_verified:
        return Response(
            {"error": "User is already verified."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    EmailVerificationToken.objects.filter(user=user).delete()

    if is_mobile:
        otp = random.randint(100000, 999999)
        EmailVerificationToken.objects.create(user=user, otp=otp)
        html_content = render_to_string(
            VERIFY_EMAIL_TEMPLATE,
            {
                "is_mobile": True,
                "full_name": f"{user.first_name} {user.last_name}",
                "otp": otp,
            },
        )
    else:
        uuid_token = uuid.uuid4()
        request_base_url = request.build_absolute_url()

        EmailVerificationToken.objects.create(user=user, token=uuid_token)
        verify_link = f"{request_base_url}verify-email?token={uuid_token}"
        html_content = render_to_string(
            VERIFY_EMAIL_TEMPLATE,
            {
                "is_mobile": False,
                "full_name": f"{user.first_name} {user.last_name}",
                "verify_link": verify_link,
            },
        )

    verification_email = EmailMultiAlternatives(
        subject="Verify Your Email Address",
        body="",
        from_email=os.environ.get("EMAIL_HOST_USER"),
        to=[user.email],
    )
    verification_email.attach_alternative(html_content, EMAIL_CONTENT_TYPE)
    try:
        verification_email.send(fail_silently=False)
    except Exception:
        return Response(
            "Failed to send email",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return Response("OTP/Link resent successfully.", status=status.HTTP_200_OK)
