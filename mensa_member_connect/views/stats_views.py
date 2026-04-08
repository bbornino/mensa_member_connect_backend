# mensa_member_connect/views/stats_views.py

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from mensa_member_connect.models.custom_user import CustomUser
from mensa_member_connect.views.custom_user_views import CustomUserViewSet
from mensa_member_connect.models.expertise import Expertise
from mensa_member_connect.models.connection_request import ConnectionRequest


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def stats(request):
    """
    Returns counts for dashboard:
    - active users
    - total experts
    - total expertise records
    - total connection requests
    """
    user_viewset = CustomUserViewSet()

    data = {
        "active_users": CustomUser.objects.filter(status="active").count(),
        "total_experts": user_viewset.list_experts_raw().filter(status="active").count(),
        "total_expertise": Expertise.objects.filter(user__status="active").count(),
        "total_connection_requests": ConnectionRequest.objects.count(),
    }
    return Response(data)
