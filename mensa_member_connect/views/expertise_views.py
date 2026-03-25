# mensa_member_connect/views/expertise_views.py
import logging
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

logger = logging.getLogger(__name__)

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
        try:
            # IMPORTANT: keep this endpoint cheap and bounded.
            # - `list(EntireQuerySet)` OOMs small containers (homepage traffic).
            # - `order_by("?")` is ORDER BY RANDOM() on Postgres: full-table scan + sort on large
            #   tables — workers time out or the DB pegs; Railway often surfaces that as HTTP 500
            #   with an empty body.
            pool = list(
                Expertise.objects.filter(
                    what_offering__isnull=False,
                    area_of_expertise__isnull=False,
                    user__status="active",
                )
                .exclude(what_offering="")
                .select_related("area_of_expertise")
                .order_by("-id")[:200]
            )
            k = min(18, len(pool))
            sampled = random.sample(pool, k) if k else []

            data = [
                {
                    "industry": (e.area_of_expertise.industry_name if e.area_of_expertise else ""),
                    "what_offering": (e.what_offering or ""),
                }
                for e in sampled
            ]
            return Response(data)
        except Exception:
            # Fail "soft" for the public homepage; return empty sample rather than 500/crash.
            logger.exception("Failed to generate public expertise sample")
            return Response([])
