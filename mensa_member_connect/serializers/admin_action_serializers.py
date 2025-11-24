# mensa_member_connect/serializers/admin_action_serializers.py
from rest_framework import serializers
from mensa_member_connect.models.admin_action import AdminAction
from mensa_member_connect.serializers.custom_user_serializers import (
    CustomUserMiniSerializer,
)


# List serializer (lightweight)
class AdminActionListSerializer(serializers.ModelSerializer):
    admin_id = serializers.IntegerField(source="admin.id", read_only=True)
    admin_name = serializers.CharField(source="admin.get_full_name", read_only=True)
    user_id = serializers.IntegerField(source="target_user.id", read_only=True)
    user_name = serializers.CharField(
        source="target_user.get_full_name", read_only=True
    )

    class Meta:
        model = AdminAction
        fields = [
            "id",
            "admin_id",
            "admin_name",
            "user_id",
            "user_name",
            "action",
            "created_at",
        ]


# Detail serializer (all fields)
class AdminActionDetailSerializer(serializers.ModelSerializer):
    admin = CustomUserMiniSerializer(source="admin_id", read_only=True)
    user = CustomUserMiniSerializer(source="target_user_id", read_only=True)

    class Meta:
        model = AdminAction
        fields = "__all__"
