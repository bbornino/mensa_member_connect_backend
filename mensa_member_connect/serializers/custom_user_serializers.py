# mensa_member_connect/serializers/custom_user_serializers.py
import base64
import re
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
    is_expert = serializers.BooleanField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "member_id",
            "role",
            "status",
            "local_group",
            "is_expert",
        ]


class CustomUserDetailSerializer(serializers.ModelSerializer):
    industry = IndustryListSerializer(read_only=True)
    phone = DRFPhoneNumberField(region="US", required=False, allow_null=True)
    local_group = LocalGroupMiniSerializer(read_only=True)
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
    occupation = serializers.CharField(required=False, allow_blank=True)

    local_group_name = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        exclude = ["profile_photo"]
        read_only_fields = ["id"]

    def to_internal_value(self, data):
        """
        Normalize phone number before validation.
        Accepts various formats (e.g., "(555) 123-4567", "555-123-4567", "5551234567")
        and converts to E.164 format (+15551234567).
        If phone is invalid and optional, it will be removed from the data.
        This ensures consistent phone number handling across all forms.
        """
        # Make data mutable if it's not already
        if hasattr(data, "_mutable"):
            data._mutable = True
        elif not isinstance(data, dict):
            data = dict(data)
        else:
            data = data.copy()

        # Get the phone value if present
        phone_value = data.get("phone")
        if phone_value and isinstance(phone_value, str):
            phone_value = phone_value.strip()

            # If empty after stripping, remove it (phone is optional)
            if not phone_value:
                data.pop("phone", None)
            # If already in E.164 format (starts with +), use as-is
            elif phone_value.startswith("+"):
                # Already in E.164 format, keep it
                pass
            else:
                try:
                    # Remove all non-numeric characters
                    digits = re.sub(r"\D", "", phone_value)

                    # Remove leading 1 if present (US country code)
                    if len(digits) == 11 and digits.startswith("1"):
                        digits = digits[1:]

                    # If we have exactly 10 digits, convert to E.164 format
                    if len(digits) == 10:
                        data["phone"] = f"+1{digits}"
                    else:
                        # Invalid phone number - since phone is optional, remove it
                        # This prevents validation errors for invalid phone numbers
                        data.pop("phone", None)
                except Exception:
                    # If conversion fails, remove phone since it's optional
                    data.pop("phone", None)

        return super().to_internal_value(data)

    def get_local_group_name(self, obj):
        if obj.local_group:
            return obj.local_group.group_name  # no "- 94"
        return None

    def get_photo(self, obj):
        if not obj.profile_photo:
            return None

        photo_bytes = bytes(obj.profile_photo)
        image_format = _detect_image_format(photo_bytes)
        base64_data = base64.b64encode(photo_bytes).decode("utf-8")
        return f"data:image/{image_format};base64,{base64_data}"


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, help_text="Password reset token from email")
    new_password = serializers.CharField(
        required=True,
        min_length=8,
        write_only=True,
        help_text="New password (minimum 8 characters)"
    )
    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        help_text="Confirm new password"
    )

    def validate(self, data):
        """Validate that passwords match"""
        if data.get('new_password') != data.get('confirm_password'):
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })
        return data
