# mensa_member_connect/serializers/custom_user_serializers.py
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField as DRFPhoneNumberField

# from django.conf import settings
from mensa_member_connect.models.custom_user import CustomUser
from mensa_member_connect.models.local_group import LocalGroup

from mensa_member_connect.serializers.local_group_serializers import (
    LocalGroupMiniSerializer,
)

from mensa_member_connect.serializers.industry_serializers import IndustryListSerializer
from mensa_member_connect.serializers.expertise_serializers import (
    ExpertiseDetailSerializer,
)


class CustomUserExpertSerializer(serializers.ModelSerializer):
    industry = IndustryListSerializer(read_only=True)
    local_group = LocalGroupMiniSerializer(read_only=True)
    expertise = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "city",
            "state",
            "occupation",
            "industry",
            "background",
            "availability_status",
            "show_contact_info",
            "local_group",
            "expertise",
        ]

    def get_expertise(self, obj):
        # Use prefetched expertises to avoid N+1 queries
        expertises = obj.expertises.all()
        return ExpertiseDetailSerializer(expertises, many=True).data


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
    industry = IndustryListSerializer(read_only=True)
    phone = DRFPhoneNumberField(region="US", required=False, allow_null=True)
    local_group_id = serializers.PrimaryKeyRelatedField(
        queryset=LocalGroup.objects.all(),
        source="local_group",
        write_only=True,
        required=False,
        allow_null=True,
    )

    local_group_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = "__all__"

    def get_local_group_name(self, obj):
        if obj.local_group:
            return obj.local_group.group_name  # no "- 94"
        return None
