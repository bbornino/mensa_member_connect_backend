# mensa_member_connect/views/expertise_views.py
import random

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
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
        action = getattr(self, 'action', None)
        if action in ["list"]:
            return ExpertiseListSerializer
        return ExpertiseDetailSerializer

    @action(detail=False, methods=["get"], url_path="by_user/(?P<user_id>[^/.]+)")
    def by_user(self, request, user_id=None):
        """
        Return all expertise records belonging to a given user.
        Requires authentication to view expert profiles.
        """
        queryset = Expertise.objects.filter(user_id=user_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        url_path="sample",
        permission_classes=[AllowAny],
        authentication_classes=[],
    )
    def sample(self, request):
        """
        Return a public sample of expertise records with no PII.
        Used on the homepage to tease the variety of available expertise.
        """
        pool = list(
            Expertise.objects.filter(
                what_offering__isnull=False,
                area_of_expertise__isnull=False,
                user__status="active",
            )
            .exclude(what_offering="")
            .select_related("area_of_expertise")
        )
        sample_size = min(18, len(pool))
        sampled = random.sample(pool, sample_size) if len(pool) >= sample_size else pool
        data = [
            {
                "industry": e.area_of_expertise.industry_name,
                "what_offering": e.what_offering,
            }
            for e in sampled
        ]
        return Response(data)
