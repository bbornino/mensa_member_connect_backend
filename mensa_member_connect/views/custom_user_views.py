# mensa_member_connect/views/custom_user_views.py
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.db.models import Exists, OuterRef
from mensa_member_connect.models.custom_user import CustomUser
from mensa_member_connect.models.expertise import Expertise
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

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        if self.action == "list_all_users":
            return [IsAdminRole()]
        if self.action in ["authenticate_user", "register_user", "list_experts"]:
            return []  # public endpoints, no auth required
        return [IsAuthenticated()]

    @action(detail=False, methods=["post"], url_path="authenticate")
    def authenticate_user(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response(
                {"error": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": CustomUserDetailSerializer(user).data,
                }
            )
        return Response(
            {"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED
        )

    @action(detail=False, methods=["post"], url_path="logout")
    def logout_user(self, request):
        refresh_token = request.data.get("refresh")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({"detail": "Successfully logged out."})
            except Exception:  # TODO: narrow this exception later
                return Response(
                    {"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            {"detail": "No refresh token provided."}, status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=["get"], url_path="me")
    def user_profile(self, request):
        user = request.user
        serializer = CustomUserDetailSerializer(user)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        # @action(detail=False, methods=["patch"], url_path="update")
        user = self.request.user  # the requesting user (admin or self)
        target_user = self.get_object()  # the user being updated

        logger.info(
            "[USER_UPDATE] User %s attempting to update target user ID=%s",
            user.username,
            target_user.id,
        )

        old_status = target_user.status

        serializer = CustomUserDetailSerializer(
            target_user, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            print("After save:", target_user.status)

            logger.info(
                "[USER_UPDATE] Successfully updated user ID=%s by user %s. Status was: %s. Status is now: %s",
                target_user.id,
                user.username,
                old_status,
                target_user.status,
            )

            target_user.refresh_from_db()

            # Send email if status changed to active
            if old_status != "active" and target_user.status == "active":

                try:
                    notify_user_approval(target_user.email, target_user.get_full_name())
                    logger.info(
                        "[EMAIL] Sent approval notification to user: %s",
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
            user.username,
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
        username = request.data.get("username")
        email = request.data.get("email")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        password = request.data.get("password")

        logger.info(
            "[USER_REG] Attempting registration for username=%s, email=%s",
            username,
            email,
        )

        if not all([username, email, first_name, last_name, password]):
            logger.warning(
                "[USER_REG] Registration failed: missing fields for email=%s", email
            )
            return Response(
                {"error": "All fields are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if CustomUser.objects.filter(username=username).exists():
            logger.warning(
                "[USER_REG] Registration failed: username already exists: %s", username
            )
            return Response(
                {"error": "Username already exists."},
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

        new_user = CustomUser.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )

        logger.info(
            "[USER_REG] Successfully created user: username=%s, email=%s",
            username,
            email,
        )

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
        return Response(serializer.data)


class TokenRefreshCustomView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except Exception:  # TODO: narrow this exception later
            return Response(
                {"detail": "Token refresh failed."}, status=status.HTTP_401_UNAUTHORIZED
            )
