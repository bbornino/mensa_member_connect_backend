from rest_framework import serializers
from mensa_member_connect.models.local_group import LocalGroup


# List serializer (lightweight)
class LocalGroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalGroup
        fields = "__all__"


class LocalGroupMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = LocalGroup
        fields = ["group_name"]


# Detail serializer (all fields)
class LocalGroupDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalGroup
        fields = "__all__"
