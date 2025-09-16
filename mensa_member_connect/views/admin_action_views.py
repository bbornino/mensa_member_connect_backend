from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from mensa_member_connect.models.admin_action import AdminAction
from mensa_member_connect.serializers.admin_action_serializers import (
    AdminActionDetailSerializer,
    AdminActionListSerializer,
)


class AdminActionViewSet(viewsets.ModelViewSet):
    queryset = AdminAction.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return AdminActionListSerializer
        elif self.action == "retrieve":
            return AdminActionDetailSerializer
        return AdminActionDetailSerializer
