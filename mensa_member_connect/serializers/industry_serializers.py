from rest_framework import serializers
from mensa_member_connect.models.industry import Industry


# List serializer (lightweight)
class IndustryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ["id", "industry_name"]


class IndustryMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ["industry_name"]  # keep it minimal


# Detail serializer (all fields)
class IndustryDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Industry
        fields = "__all__"
