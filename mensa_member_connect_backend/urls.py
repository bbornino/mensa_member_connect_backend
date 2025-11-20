# mensa_member_connect/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authentication import BaseAuthentication

from mensa_member_connect.views.custom_user_views import CustomUserViewSet
from mensa_member_connect.views.custom_user_auth_views import (
    AuthenticateUserView,
    PasswordResetRequestView,
    LogoutUserView,
    TokenRefreshCustomView,
)
from mensa_member_connect.views.custom_user_registration_views import (
    CustomUserRegistrationViewSet,
)
from mensa_member_connect.views.expertise_views import ExpertiseViewSet
from mensa_member_connect.views.connection_request_views import ConnectionRequestViewSet
from mensa_member_connect.views.industry_views import IndustryViewSet
from mensa_member_connect.views.local_group_views import LocalGroupViewSet
from mensa_member_connect.views.admin_action_views import AdminActionViewSet


class NoAuth(BaseAuthentication):
    def authenticate(self, request):
        return None


# Create a DRF router and register all your viewsets
router = DefaultRouter()
router.register(r"users", CustomUserViewSet, basename="user")
router.register(r"expertises", ExpertiseViewSet, basename="expertise")
router.register(
    r"connection_requests", ConnectionRequestViewSet, basename="connection_request"
)
router.register(r"industries", IndustryViewSet, basename="industry")
router.register(r"local_groups", LocalGroupViewSet, basename="local_group")
router.register(r"admin_actions", AdminActionViewSet, basename="admin_action")

# Include the router URLs in urlpatterns
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/refresh/", TokenRefreshCustomView.as_view(), name="token_refresh"),
    path(
        "api/users/authenticate/",
        AuthenticateUserView.as_view(),
        name="user-authenticate",
    ),
    path(
        "api/users/password-reset-request/",
        PasswordResetRequestView.as_view(),
        name="user-password-reset-request",
    ),
    path(
        "api/users/register/",
        CustomUserRegistrationViewSet.as_view({"post": "register_user"}),
        name="user-register",
    ),
    path("api/users/logout/", LogoutUserView.as_view(), name="user-logout"),
    path("api/", include(router.urls)),
]
