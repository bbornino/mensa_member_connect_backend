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
    - total users
    - total experts
    - total expertise records
    - total connection requests
    """
    user_viewset = CustomUserViewSet()

    data = {
        "total_users": CustomUser.objects.count(),
        "total_experts": user_viewset.list_experts_raw().count(),
        "total_expertise": Expertise.objects.count(),
        "total_connection_requests": ConnectionRequest.objects.count(),
    }
    return Response(data)
