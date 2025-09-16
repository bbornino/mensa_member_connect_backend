from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from mensa_member_connect.models.local_group import LocalGroup
from mensa_member_connect.serializers.local_group_serializers import (
    LocalGroupListSerializer,
    LocalGroupDetailSerializer,
)


class LocalGroupViewSet(viewsets.ModelViewSet):
    queryset = LocalGroup.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return LocalGroupListSerializer
        elif self.action == "retrieve":
            return LocalGroupDetailSerializer
        return LocalGroupDetailSerializer
