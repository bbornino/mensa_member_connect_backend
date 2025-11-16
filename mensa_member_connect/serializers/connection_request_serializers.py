from rest_framework import serializers
from mensa_member_connect.models.connection_request import ConnectionRequest
from mensa_member_connect.models.custom_user import CustomUser
from mensa_member_connect.serializers.custom_user_serializers import (
    CustomUserMiniSerializer,
)


# List serializer (lightweight)
class ConnectionRequestListSerializer(serializers.ModelSerializer):
    expert = CustomUserMiniSerializer(source="expert_id", read_only=True)
    seeker = CustomUserMiniSerializer(source="seeker_id", read_only=True)

    class Meta:
        model = ConnectionRequest
        fields = ["expert", "seeker", "created_at"]


# Detail serializer (all fields)
class ConnectionRequestDetailSerializer(serializers.ModelSerializer):
    # For reading
    expert = CustomUserMiniSerializer(read_only=True)
    seeker = CustomUserMiniSerializer(read_only=True)

    # For writing
    expert_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), write_only=True, source="expert"
    )

    class Meta:
        model = ConnectionRequest
        fields = "__all__"
