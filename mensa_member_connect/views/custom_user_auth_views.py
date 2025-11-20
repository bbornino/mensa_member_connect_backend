# mensa_member_connect/views/custom_user_auth_views.py

import logging
from django.contrib.auth import authenticate
from django.utils.crypto import get_random_string
from django.core.cache import cache
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import BaseAuthentication

from mensa_member_connect.models.custom_user import CustomUser
from mensa_member_connect.serializers.custom_user_serializers import (
    PasswordResetRequestSerializer,
    CustomUserDetailSerializer,
)
from mensa_member_connect.utils.email_utils import send_password_reset_email

logger = logging.getLogger(__name__)


class NoAuth(BaseAuthentication):
    def authenticate(self, request):
        return None


class AuthenticateUserView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        logger.debug("request.data=%s", request.data)
        email = request.data.get("email") or request.data.get("username")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            logger.warning(
                "Authentication failed: invalid password for email=%s", email
            )
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            logger.info("User authenticated successfully: %s", email)

            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": CustomUserDetailSerializer(user).data,
                }
            )

        logger.warning("Authentication failed: invalid password for email=%s", email)
        return Response(
            {"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED
        )


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        """
        Accepts an email and sends a password reset link if the user exists.
        """
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data.get("email")  # type: ignore

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            # Do not reveal whether email exists
            return Response(
                {"message": "If that email exists, a reset message will be sent."}
            )

        # generate token and cache it for 1 hour
        token = get_random_string(64)
        cache.set(f"pwreset:{token}", user.id, timeout=3600)

        # prepare reset link
        reset_link = (
            f"{request.scheme}://{request.get_host()}/reset-password?token={token}"
        )

        logger.debug("Password reset token generated for user_id=%s", user.id)

        # send email
        try:
            send_password_reset_email(email, user.get_full_name(), reset_link)
            logger.info("Password reset email sent to: %s", email)
        except Exception as e:
            logger.error("Failed to send password reset email to %s: %s", email, e)

        return Response(
            {"message": "If that email exists, a reset message will be sent."}
        )


class LogoutUserView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "No refresh token provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info("User logged out successfully: user_id=%s", request.user.id)
            return Response({"detail": "Successfully logged out."})
        except Exception as e:
            logger.warning("Logout failed: %s", e)
            return Response(
                {"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
            )


class TokenRefreshCustomView(TokenRefreshView):
    """
    Custom Token Refresh View to handle exceptions gracefully.
    """

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except Exception as e:
            logger.warning("Token refresh failed: %s", e)
            return Response(
                {"detail": "Token refresh failed."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
