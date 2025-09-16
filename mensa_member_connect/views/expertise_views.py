# mensa_member_connect/views/expertise_views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from mensa_member_connect.models.expertise import Expertise
from mensa_member_connect.serializers.expertise_serializers import (
    ExpertiseListSerializer,
    ExpertiseDetailSerializer,
)


class ExpertiseViewSet(viewsets.ModelViewSet):
    queryset = Expertise.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return ExpertiseListSerializer
        elif self.action == "retrieve":
            return ExpertiseDetailSerializer
        return ExpertiseDetailSerializer
