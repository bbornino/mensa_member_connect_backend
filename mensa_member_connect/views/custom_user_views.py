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
        if self.action in ["authenticate_user", "register_user", "list_experts"]:
            return []  # public endpoints, no auth required
        return [IsAuthenticated()]

    @action(detail=False, methods=["get"], url_path="me")
    def user_profile(self, request):
        user = request.user
        serializer = CustomUserDetailSerializer(user)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        # @action(detail=False, methods=["patch"], url_path="update")
        if "username" in request.data:
            return Response(
                {"error": "Username cannot be changed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = self.request.user  # the requesting user (admin or self)
        target_user = self.get_object()  # the user being updated

        logger.info(
            "[USER_UPDATE] User %s attempting to update target user ID=%s",
            user.get_full_name() or f"{user.first_name} {user.last_name}",
            target_user.id,
        )

        old_status = target_user.status

        serializer = CustomUserDetailSerializer(
            target_user, data=request.data, partial=True
        )

        if serializer.is_valid():
            new_email = request.data.get("email")
            if new_email:
                target_user.username = new_email.lower().strip()

            serializer.save()
            print("After save:", target_user.status)

            logger.info(
                "[USER_UPDATE] Successfully updated user ID=%s by user %s. Status was: %s. Status is now: %s",
                target_user.id,
                user.get_full_name() or f"{user.first_name} {user.last_name}",
                old_status,
                target_user.status,
            )

            target_user.refresh_from_db()

            # Send email if status changed to active
            if old_status != "active" and target_user.status == "active":

                try:
                    notify_user_approval(target_user.email, target_user.get_full_name())
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

    @action(
        detail=False,
        methods=["get"],
        url_path="experts",
        permission_classes=[],  # Make it public
    )
    def list_experts(self, request):
        """
        Returns all users who are 'experts'.
        Defined as having at least one expertise record.
        """
        experts = (
            CustomUser.objects.filter(expertises__isnull=False)
            .distinct()
            .select_related("industry", "local_group")
            .prefetch_related("expertises__area_of_expertise")
        )
        serializer = CustomUserExpertSerializer(experts, many=True)
        logger.info("[LIST_EXPERTS] Returning %d experts", experts.count())
        return Response(serializer.data)
