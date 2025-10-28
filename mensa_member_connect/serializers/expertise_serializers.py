from rest_framework import serializers
from mensa_member_connect.models.expertise import Expertise


# List serializer (lightweight)
class ExpertiseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expertise
        fields = ["id", "what_offering"]


# Detail serializer (all fields)
class ExpertiseDetailSerializer(serializers.ModelSerializer):
    area_of_expertise_name = serializers.CharField(source='area_of_expertise.industry_name', read_only=True)

    class Meta:
        model = Expertise
        fields = "__all__"
