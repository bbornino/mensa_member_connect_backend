# mensa_member_connect/views/expertise_views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response


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
        if self.action in ["list", "by_user"]:
            return ExpertiseListSerializer
        return ExpertiseDetailSerializer

    @action(detail=False, methods=["get"], url_path="by_user/(?P<user_id>[^/.]+)")
    def by_user(self, request, user_id=None):
        """
        Return all expertise records belonging to a given user.
        """
        queryset = Expertise.objects.filter(user_id=user_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
