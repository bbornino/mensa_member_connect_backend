from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from mensa_member_connect.models.connection_request import ConnectionRequest
from mensa_member_connect.serializers.connection_request_serializers import (
    ConnectionRequestDetailSerializer,
    ConnectionRequestListSerializer,
)


class ConnectionRequestViewSet(viewsets.ModelViewSet):
    queryset = ConnectionRequest.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return ConnectionRequestListSerializer
        elif self.action == "retrieve":
            return ConnectionRequestDetailSerializer
        return ConnectionRequestDetailSerializer
