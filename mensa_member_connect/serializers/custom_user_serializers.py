# mensa_member_connect/serializers/custom_user_serializers.py
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField as DRFPhoneNumberField

# from django.conf import settings
from mensa_member_connect.models.custom_user import CustomUser
from mensa_member_connect.models.local_group import LocalGroup
from mensa_member_connect.models.expertise import Expertise


# from mensa_member_connect.models.custom_user import CustomUser
from mensa_member_connect.serializers.local_group_serializers import (
    LocalGroupMiniSerializer,
)

# from mensa_member_connect.serializers.industry_serializers import IndustryMiniSerializer
from mensa_member_connect.serializers.expertise_serializers import (
    ExpertiseDetailSerializer,
)


class CustomUserExpertSerializer(serializers.ModelSerializer):
    industry = serializers.CharField(source="industry.industry_name", read_only=True)
    expertise = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "first_name",
            "last_name",
            "city",
            "state",
            "occupation",
            "industry",
            "background",
            "availability_status",
            "show_contact_info",
            "expertise",
        ]

    def get_expertise(self, obj):
        # Grab first 2 expertises only for now
        qs = Expertise.objects.filter(user=obj)[:2]
        # Use existing serializer
        return ExpertiseDetailSerializer(qs, many=True).data


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
