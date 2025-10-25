# mensa_member_connect/serializers/custom_user_serializers.py
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField as DRFPhoneNumberField

# from django.conf import settings
from mensa_member_connect.models.custom_user import CustomUser
from mensa_member_connect.models.local_group import LocalGroup


# from mensa_member_connect.models.custom_user import CustomUser
from mensa_member_connect.serializers.local_group_serializers import (
    LocalGroupMiniSerializer,
)


class CustomUserExpertSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "first_name", "last_name", "city", "state", "occupation"]


class CustomUserMiniSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = CustomUser
        fields = ["name"]


class CustomUserListSerializer(serializers.ModelSerializer):
    local_group = LocalGroupMiniSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "member_id",
            "role",
            "status",
            "local_group",
        ]


class CustomUserDetailSerializer(serializers.ModelSerializer):
    local_group = serializers.PrimaryKeyRelatedField(
        queryset=LocalGroup.objects.all(), required=False, allow_null=True
    )
    phone = DRFPhoneNumberField(region="US", required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = "__all__"
