from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from mensa_member_connect.models.custom_user import CustomUser
from mensa_member_connect.models.connection_request import ConnectionRequest
from mensa_member_connect.serializers.connection_request_serializers import (
    ConnectionRequestDetailSerializer,
    ConnectionRequestListSerializer,
)

from mensa_member_connect.utils.email_utils import notify_expert_new_message


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

    @action(detail=False, methods=["post"], url_path="send_request")
    def send_request(self, request):
        """
        Seeker sends a connection request to an expert.
        """
        seeker = request.user
        expert_id = request.data.get("expert_id")
        message = request.data.get("message", "")

        if not expert_id:
            return Response(
                {"error": "expert_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            expert = CustomUser.objects.get(id=expert_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "Expert not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Create the connection request
        conn_request = ConnectionRequest.objects.create(
            seeker=seeker, expert=expert, message=message
        )

        # Notify the expert via email
        notify_expert_new_message(expert.email, seeker.get_full_name(), message)

        serializer = ConnectionRequestDetailSerializer(conn_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
