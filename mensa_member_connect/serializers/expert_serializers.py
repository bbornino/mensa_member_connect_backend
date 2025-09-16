# mensa_member_connect/serializers/expert_serializers.py
from rest_framework import serializers
from mensa_member_connect.models.expert import Expert
from mensa_member_connect.serializers.custom_user_serializers import (
    CustomUserDetailSerializer,
    CustomUserMiniSerializer,
)
from mensa_member_connect.serializers.industry_serializers import IndustryMiniSerializer


class ExpertListSerializer(serializers.ModelSerializer):
    user = CustomUserDetailSerializer(source="user_id", read_only=False)
    industry = IndustryMiniSerializer(source="industry_id", read_only=True)

    class Meta:
        model = Expert
        fields = ["id", "user", "industry", "occupation"]  # TODO: Update from UI Table


class ExpertMiniSerializer(serializers.ModelSerializer):
    user = CustomUserMiniSerializer(source="user_id", read_only=False)

    class Meta:
        model = Expert
        fields = ["user"]


class ExpertDetailSerializer(serializers.ModelSerializer):
    user = CustomUserDetailSerializer(source="user_id", read_only=False)
    industry = IndustryMiniSerializer(source="industry_id", read_only=True)

    class Meta:
        model = Expert
        fields = "__all__"
