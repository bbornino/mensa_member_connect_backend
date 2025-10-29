# mensa_member_connect/views/custom_user_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from mensa_member_connect.models.custom_user import CustomUser
from mensa_member_connect.serializers.custom_user_serializers import (
    CustomUserDetailSerializer,
    CustomUserListSerializer,
    CustomUserExpertSerializer,
)
from mensa_member_connect.permissions import IsAdminRole


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

    @action(detail=False, methods=["patch"], url_path="update")
    def update_user_info(self, request):
        user = request.user
        serializer = CustomUserDetailSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User info updated successfully."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="register")
    def register_user(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        password = request.data.get("password")

        if not all([username, email, first_name, last_name, password]):
            return Response(
                {"error": "All fields are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if CustomUser.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if CustomUser.objects.filter(email=email).exists():
            return Response(
                {"error": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            validate_password(password)
        except Exception as e:  # TODO: narrow this exception later
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        CustomUser.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        return Response(
            {"message": "User successfully registered."}, status=status.HTTP_201_CREATED
        )

    @action(
        detail=False, methods=["get"], url_path="all", permission_classes=[IsAdminUser]
    )
    def list_all_users(self, request):
        users = CustomUser.objects.all()
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
        experts = CustomUser.objects.filter(expertises__isnull=False).distinct().select_related(
            'industry', 'local_group'
        ).prefetch_related('expertises__area_of_expertise')
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
