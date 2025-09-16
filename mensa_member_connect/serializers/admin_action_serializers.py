from rest_framework import serializers
from mensa_member_connect.models.admin_action import AdminAction
from mensa_member_connect.serializers.custom_user_serializers import (
    CustomUserMiniSerializer,
)


# List serializer (lightweight)
class AdminActionListSerializer(serializers.ModelSerializer):
    admin = CustomUserMiniSerializer(source="admin_id", read_only=True)
    user = CustomUserMiniSerializer(source="target_user_id", read_only=True)

    class Meta:
        model = AdminAction
        fields = "__all__"  # TODO: Change later with UI


# Detail serializer (all fields)
class AdminActionDetailSerializer(serializers.ModelSerializer):
    admin = CustomUserMiniSerializer(source="admin_id", read_only=True)
    user = CustomUserMiniSerializer(source="target_user_id", read_only=True)

    class Meta:
        model = AdminAction
        fields = "__all__"
