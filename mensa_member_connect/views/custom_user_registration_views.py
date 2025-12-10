# mensa_member_connect/views/custom_user_registration_views.py
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from mensa_member_connect.models.custom_user import CustomUser

from mensa_member_connect.utils.email_utils import (
    notify_admin_new_registration,
    notify_user_registration,
)
from mensa_member_connect.views.custom_user_utils import validate_phone, get_local_group
from mensa_member_connect.serializers.custom_user_serializers import CustomUserDetailSerializer

logger = logging.getLogger(__name__)


class CustomUserRegistrationViewSet(viewsets.ViewSet):
    """
    Handles user registration only.
    Endpoint: POST /api/users/register/
    """

    @action(detail=False, methods=["post"], url_path="register")
    def register_user(self, request):

        email = request.data.get("email")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        password = request.data.get("password")
        member_id = request.data.get("member_id")
        phone = request.data.get("phone")
        city = request.data.get("city")
        state = request.data.get("state")
        local_group = request.data.get("local_group")

        logger.info(
            "[USER_REG] Attempting registration for %s %s, email=%s",
            first_name,
            last_name,
            email,
        )

        if not all([email, first_name, last_name, password]):
            logger.warning(
                "[USER_REG] Registration failed: missing fields for email=%s", email
            )
            return Response(
                {"error": "All fields are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if CustomUser.objects.filter(email=email).exists():
            logger.warning(
                "[USER_REG] Registration failed: email already exists: %s", email
            )
            return Response(
                {"error": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            validate_password(password)
        except Exception as e:  # TODO: narrow this exception later
            logger.warning(
                "[USER_REG] Registration failed: password validation failed for email=%s: %s",
                email,
                e,
            )
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare user creation data
        user_data = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "password": password,
        }

        # Add member_id if provided
        if member_id:
            try:
                user_data["member_id"] = int(member_id)
            except (ValueError, TypeError):
                logger.warning(
                    "[USER_REG] Invalid member_id format: %s for email=%s",
                    member_id,
                    email,
                )
                return Response(
                    {"error": "Member ID must be numeric."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Add phone if provided - normalize to E.164 format
        # If phone is invalid, skip it (phone is optional)
        if phone:
            try:
                user_data["phone"] = validate_phone(phone)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Add city if provided
        if city:
            user_data["city"] = city

        # Add state if provided
        if state:
            user_data["state"] = state

        # Handle local_group - can be ID (int) or name (string)
        if local_group:
            try:
                user_data["local_group"] = get_local_group(local_group, email)
            except ValueError as e:
                logger.warning("[USER_REG] %s", e)
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        new_user = CustomUser.objects.create_user(**user_data)

        logger.info("[USER_REG] Successfully created user: email=%s", email)

        # Notify admin and user
        try:
            notify_user_registration(new_user.email, new_user.get_full_name())
            logger.info(
                "[EMAIL] Sent registration confirmation to user: %s", new_user.email
            )
        except Exception as e:
            logger.error(
                "[EMAIL] Failed to send registration confirmation to user %s: %s",
                new_user.email,
                e,
            )

        try:
            notify_admin_new_registration(new_user.email, new_user.get_full_name())
            logger.info(
                "[EMAIL] Sent new registration notification to admin for user: %s",
                new_user.email,
            )
        except Exception as e:
            logger.error(
                "[EMAIL] Failed to notify admin about new user %s: %s",
                new_user.email,
                e,
            )

        # Generate JWT tokens for auto-login
        refresh = RefreshToken.for_user(new_user)
        
        # Serialize user data
        user_data = CustomUserDetailSerializer(new_user).data
        
        logger.info("[USER_REG] Returning tokens for auto-login: email=%s", email)
        
        return Response(
            {
                "message": "User successfully registered.",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": user_data,
            },
            status=status.HTTP_201_CREATED
        )
