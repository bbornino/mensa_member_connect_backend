# mensa_member_connect/serializers/custom_user_serializers.py
from rest_framework import serializers
from django.conf import settings

# from mensa_member_connect.models.custom_user import CustomUser
from mensa_member_connect.serializers.local_group_serializers import (
    LocalGroupMiniSerializer,
)


CustomUser = settings.AUTH_USER_MODEL


class CustomUserMiniSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = CustomUser
        fields = ["name"]


class CustomUserListSerializer(serializers.ModelSerializer):
    # TODO: update from UI table
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "member_id",
            "role",
            "status",
        ]


class CustomUserDetailSerializer(serializers.ModelSerializer):
    local_group = LocalGroupMiniSerializer(source="local_group_id", read_only=True)

    class Meta:
        model = CustomUser
        fields = "__all__"
