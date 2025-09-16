from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from mensa_member_connect.models.industry import Industry
from mensa_member_connect.serializers.industry_serializers import (
    IndustryListSerializer,
    IndustryDetailSerializer,
)


class IndustryViewSet(viewsets.ModelViewSet):
    queryset = Industry.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return IndustryListSerializer
        elif self.action == "retrieve":
            return IndustryDetailSerializer
        return IndustryDetailSerializer
