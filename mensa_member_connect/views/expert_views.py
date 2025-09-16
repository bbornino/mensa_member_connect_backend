from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from mensa_member_connect.models.expert import Expert
from mensa_member_connect.serializers.expert_serializers import (
    ExpertListSerializer,
    ExpertDetailSerializer,
)


class ExpertViewSet(viewsets.ModelViewSet):
    queryset = Expert.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return ExpertListSerializer
        elif self.action == "retrieve":
            return ExpertDetailSerializer
        return ExpertDetailSerializer
