# mensa_member_connect/serializers/connection_request_serializers.py
from rest_framework import serializers
from mensa_member_connect.models.connection_request import ConnectionRequest
from mensa_member_connect.models.custom_user import CustomUser
from mensa_member_connect.serializers.custom_user_serializers import (
    CustomUserSummarySerializer,
)


# List serializer (lightweight)
class ConnectionRequestListSerializer(serializers.ModelSerializer):
    expert_id = serializers.IntegerField(source="expert.id", read_only=True)
    expert_name = serializers.CharField(source="expert.get_full_name", read_only=True)

    seeker_id = serializers.IntegerField(source="seeker.id", read_only=True)
    seeker_name = serializers.CharField(source="seeker.get_full_name", read_only=True)

    class Meta:
        model = ConnectionRequest
        fields = [
            "id",
            "expert_id",
            "expert_name",
            "seeker_id",
            "seeker_name",
            "created_at",
        ]


# Detail serializer (all fields)
class ConnectionRequestDetailSerializer(serializers.ModelSerializer):
    # For reading
    expert = CustomUserSummarySerializer(read_only=True)
    seeker = CustomUserSummarySerializer(read_only=True)

    # For writing
    expert_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), write_only=True, source="expert"
    )

    class Meta:
        model = ConnectionRequest
        fields = "__all__"
