import base64

# mensa_member_connect/serializers/custom_user_serializers.py
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField as DRFPhoneNumberField

# from django.conf import settings
from mensa_member_connect.models.custom_user import CustomUser
from mensa_member_connect.models.local_group import LocalGroup
from mensa_member_connect.models.industry import Industry

from mensa_member_connect.serializers.local_group_serializers import (
    LocalGroupMiniSerializer,
)

from mensa_member_connect.serializers.industry_serializers import IndustryListSerializer
from mensa_member_connect.serializers.expertise_serializers import (
    ExpertiseDetailSerializer,
)


def _detect_image_format(photo_bytes: bytes) -> str:
    if photo_bytes.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if photo_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if photo_bytes.startswith(b"GIF87a") or photo_bytes.startswith(b"GIF89a"):
        return "gif"
    return "jpeg"


class CustomUserExpertSerializer(serializers.ModelSerializer):
    industry = IndustryListSerializer(read_only=True)
    local_group = LocalGroupMiniSerializer(read_only=True)
    expertise = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()

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
            "photo",
        ]

    def get_expertise(self, obj):
        # Use prefetched expertises to avoid N+1 queries
        expertises = obj.expertises.all()
        return ExpertiseDetailSerializer(expertises, many=True).data

    def get_photo(self, obj):
        if not obj.profile_photo:
            return None

        photo_bytes = bytes(obj.profile_photo)
        image_format = _detect_image_format(photo_bytes)
        base64_data = base64.b64encode(photo_bytes).decode("utf-8")
        return f"data:image/{image_format};base64,{base64_data}"


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
    industry_id = serializers.PrimaryKeyRelatedField(
        queryset=Industry.objects.all(),
        source="industry",
        write_only=True,
        required=False,
        allow_null=True,
    )

    local_group_name = serializers.SerializerMethodField()
    profile_photo = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = "__all__"

    def get_local_group_name(self, obj):
        if obj.local_group:
            return obj.local_group.group_name  # no "- 94"
        return None

    def get_profile_photo(self, obj):
        if obj.profile_photo:
            # If using BinaryField, base64 encode it
            import base64

            return base64.b64encode(obj.profile_photo).decode("utf-8")
        return None
