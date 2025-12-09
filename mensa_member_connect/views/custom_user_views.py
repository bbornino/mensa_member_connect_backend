# mensa_member_connect/views/custom_user_views.py
import logging
import re
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.password_validation import validate_password
from django.db.models import Exists, OuterRef
from mensa_member_connect.models.custom_user import CustomUser
from mensa_member_connect.models.expertise import Expertise
from mensa_member_connect.models.local_group import LocalGroup
from mensa_member_connect.models.admin_action import AdminAction

from mensa_member_connect.serializers.custom_user_serializers import (
    CustomUserDetailSerializer,
    CustomUserListSerializer,
    CustomUserExpertSerializer,
)
from mensa_member_connect.permissions import IsAdminRole
from mensa_member_connect.utils.email_utils import (
    notify_admin_new_registration,
    notify_user_registration,
    notify_user_approval,
)


logger = logging.getLogger(__name__)


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserDetailSerializer
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        """
        Optimize queries by using select_related for foreign key relationships.
        This prevents N+1 queries when accessing local_group and industry.
        """
        return CustomUser.objects.select_related("local_group", "industry")

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        if self.action == "list_all_users":
            return [IsAdminRole()]
        if self.action in ["authenticate_user", "register_user"]:
            return []  # public endpoints, no auth required
        return [IsAuthenticated()]

    @action(detail=False, methods=["get"], url_path="me")
    def user_profile(self, request):
        user = request.user
        serializer = CustomUserDetailSerializer(user)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        user = self.request.user  # the requesting user (admin or self)
        target_user = self.get_object()  # the user being updated

        logger.info(
            "[USER_UPDATE] User %s attempting to update target user ID=%s",
            user.get_full_name() or f"{user.first_name} {user.last_name}",
            target_user.id,
        )

        old_status = target_user.status
        old_role = target_user.role

        serializer = CustomUserDetailSerializer(
            target_user, data=request.data, partial=True
        )

        if serializer.is_valid():

            serializer.save()
            print("After save:", target_user.status)

            # --- AdminAction Logging ---
            if old_status != target_user.status:
                action_message = (
                    f"Admin {user.get_full_name()} changed the status of user "
                    f"{target_user.id} - {target_user.get_full_name()} "
                    f"from '{old_status}' to '{target_user.status}'."
                )
                AdminAction.objects.create(
                    admin=user,
                    target_user=target_user,
                    action=action_message,
                )
                logger.info("[ADMIN_ACTION] %s", action_message)

            logger.info(
                "[USER_UPDATE] Successfully updated user ID=%s by user %s. Status was: %s. Status is now: %s",
                target_user.id,
                user.get_full_name() or f"{user.first_name} {user.last_name}",
                old_status,
                target_user.status,
            )

            if old_role != target_user.role:
                role_change_message = (
                    f"Admin {user.get_full_name()} changed the role of user "
                    f"{target_user.id} - {target_user.get_full_name()} "
                    f"from '{old_role}' to '{target_user.role}'."
                )

                AdminAction.objects.create(
                    admin=user,
                    target_user=target_user,
                    action=role_change_message,
                )

                logger.info("[ADMIN_ACTION] %s", role_change_message)

            target_user.refresh_from_db()

            # Send email if status changed to active
            if old_status != "active" and target_user.status == "active":

                try:
                    notify_user_approval(
                        target_user.email,
                        target_user.get_full_name(),
                        first_name=target_user.first_name,
                        last_name=target_user.last_name,
                    )
                    logger.info(
                        "[EMAIL] Sent approval notification to user: %s with email: %s",
                        user.get_full_name() or f"{user.first_name} {user.last_name}",
                        target_user.email,
                    )
                except Exception as e:
                    logger.error(
                        "[EMAIL] Failed to send approval notification to user %s: %s",
                        target_user.email,
                        e,
                    )

            return Response({"message": "User info updated successfully."})

        logger.warning(
            "[USER_UPDATE] Validation errors when updating user ID=%s by user %s: %s",
            target_user.id,
            user.get_full_name() or f"{user.first_name} {user.last_name}",
            serializer.errors,
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=["post"],
        url_path="photo",
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload_photo(self, request, pk=None):
        """
        Uploads and stores a user's profile photo as binary data.
        Endpoint: POST /api/users/{id}/photo/
        """
        user = self.get_object()
        file = request.FILES.get("profile_photo")

        if not file:
            return Response(
                {"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Validate file size (2MB limit)
        MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB in bytes
        if file.size > MAX_FILE_SIZE:
            return Response(
                {"error": "Image file size must be less than 2MB."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate file type
        valid_content_types = ["image/jpeg", "image/jpg", "image/png", "image/gif"]
        if file.content_type not in valid_content_types:
            return Response(
                {"error": "Please upload a JPG, PNG, or GIF image."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Read file bytes into the BinaryField
            user.profile_photo = file.read()
            user.save()

            logger.info(
                "[PHOTO_UPLOAD] User ID=%s uploaded photo (%d bytes, type=%s)",
                user.id,
                file.size,
                file.content_type,
            )

            return Response(
                {"message": "Profile photo uploaded successfully."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
            "[USER_REG] Attempting registration for email=%s",
            email,
        )

        if not all([email, first_name, last_name, password]):
            logger.warning(
                "[USER_REG] Registration failed: missing fields for email=%s", email
            )
            return Response(
                {"error": "Email, first name, last name, and password are required."},
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
            phone_value = str(phone).strip()
            if phone_value:
                # If not already in E.164 format, convert it
                if not phone_value.startswith("+"):
                    try:
                        # Remove all non-numeric characters
                        digits = re.sub(r"\D", "", phone_value)
                        # Remove leading 1 if present (US country code)
                        if len(digits) == 11 and digits.startswith("1"):
                            digits = digits[1:]
                        # If we have exactly 10 digits, convert to E.164 format
                        if len(digits) == 10:
                            user_data["phone"] = f"+1{digits}"
                        # If invalid format, skip it (phone is optional)
                    except Exception:
                        # If conversion fails, skip it (phone is optional)
                        pass
                else:
                    # Already in E.164 format
                    user_data["phone"] = phone_value

        # Add city if provided
        if city:
            user_data["city"] = city

        # Add state if provided
        if state:
            user_data["state"] = state

        # Handle local_group - can be ID (int) or name (string)
        local_group_obj = None
        if local_group:
            try:
                # Try as ID first
                if isinstance(local_group, int) or (
                    isinstance(local_group, str) and local_group.isdigit()
                ):
                    local_group_obj = LocalGroup.objects.get(id=int(local_group))
                else:
                    # Try as name
                    local_group_obj = LocalGroup.objects.get(group_name=local_group)
                user_data["local_group"] = local_group_obj
            except LocalGroup.DoesNotExist:
                logger.warning(
                    "[USER_REG] Local group not found: %s for email=%s",
                    local_group,
                    email,
                )
                return Response(
                    {"error": f"Local group '{local_group}' not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception as e:
                logger.warning(
                    "[USER_REG] Error looking up local group %s for email=%s: %s",
                    local_group,
                    email,
                    e,
                )
                return Response(
                    {"error": "Invalid local group."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        new_user = CustomUser.objects.create_user(**user_data)

        logger.info(
            "[USER_REG] Successfully created user: email=%s",
            email,
        )

        # Notify admin and user
        try:
            notify_user_registration(
                new_user.email,
                new_user.get_full_name(),
                first_name=new_user.first_name,
                last_name=new_user.last_name,
            )
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
            notify_admin_new_registration(
                new_user.email,
                new_user.get_full_name(),
                first_name=new_user.first_name,
                last_name=new_user.last_name,
            )
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

        return Response(
            {"message": "User successfully registered."}, status=status.HTTP_201_CREATED
        )

    @action(
        detail=False, methods=["get"], url_path="all", permission_classes=[IsAdminUser]
    )
    def list_all_users(self, request):
        expertise_exists = Expertise.objects.filter(user=OuterRef("pk"))
        users = (
            CustomUser.objects.all()
            .annotate(is_expert=Exists(expertise_exists))
            .select_related("local_group")
        )
        serializer = CustomUserListSerializer(users, many=True)
        logger.info("[LIST_USERS] Returning %d users", users.count())
        return Response(serializer.data)

    def list_experts_raw(self):
        """
        Returns all users who are 'experts'.
        Defined as having at least one expertise record.
        Returns the queryset of users who are experts.
        Centralizes the logic for 'who is an expert'.
        """
        qs = (
            CustomUser.objects.filter(expertises__isnull=False)
            .distinct()
            .select_related("industry", "local_group")
            .prefetch_related("expertises__area_of_expertise")
        )
        return qs

    @action(
        detail=False,
        methods=["get"],
        url_path="experts",
        permission_classes=[IsAuthenticated],  # Requires authentication
    )
    def list_experts(self, request):
        """
        Returns all users who are 'experts' to REST endpoint.
        Requires authentication to view experts.
        """
        experts = self.list_experts_raw()
        serializer = CustomUserExpertSerializer(experts, many=True)
        logger.info("[LIST_EXPERTS] Returning %d experts", experts.count())
        return Response(serializer.data)
