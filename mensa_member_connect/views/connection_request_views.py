# mensa_member_connect/views/connection_request_views.py
import logging

# from rest_framework.decorators import action
# from rest_framework.response import Response
# from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication

from mensa_member_connect.models.custom_user import CustomUser
from mensa_member_connect.models.connection_request import ConnectionRequest
from mensa_member_connect.serializers.connection_request_serializers import (
    ConnectionRequestDetailSerializer,
    ConnectionRequestListSerializer,
)

from mensa_member_connect.utils.email_utils import notify_expert_new_message

logger = logging.getLogger(__name__)


class ConnectionRequestViewSet(viewsets.ModelViewSet):
    queryset = ConnectionRequest.objects.all()
    serializer_class = ConnectionRequestDetailSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return ConnectionRequestListSerializer
        elif self.action == "retrieve":
            return ConnectionRequestDetailSerializer
        return ConnectionRequestDetailSerializer

    def perform_create(self, serializer):
        try:
            user: CustomUser = self.request.user  # type: ignore[assignment]

            if not user.is_authenticated:
                raise PermissionDenied(
                    "You must be logged in to send a connection request."
                )

            expert = serializer.validated_data.get("expert")

            if expert is None:
                logger.error(
                    "Attempted to create a connection request without an expert. Payload: %s",
                    self.request.data,  # type: ignore[assignment]
                )
                raise PermissionDenied("A valid expert must be specified.")

            conn_request = serializer.save(seeker=self.request.user)
            seeker_id = getattr(user, "id", "unknown")
            expert_id = getattr(getattr(conn_request, "expert", None), "id", "unknown")

            logger.info(
                "ConnectionRequest %s saved successfully for seeker %s → expert %s",
                conn_request.id,
                seeker_id,
                expert_id,
            )

            expert_email = conn_request.expert.email
            seeker_name = user.get_full_name()
            message = conn_request.message
            notify_expert_new_message(expert_email, seeker_name, message)
            logger.info(
                "Connection request %s sent from user %s to expert %s %s",
                conn_request.id,
                seeker_name,
                conn_request.expert.id,
                expert_email,
            )
        except Exception as e:
            seeker_id = getattr(getattr(self.request, "user", None), "id", "unknown")
            logger.error(
                "Failed to create connection request for user %s: %s", seeker_id, e
            )
            raise
