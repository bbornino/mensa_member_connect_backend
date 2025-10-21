from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from mensa_member_connect.models.custom_user import CustomUser
from mensa_member_connect.models.admin_action import AdminAction
from mensa_member_connect.models.connection_request import ConnectionRequest
from mensa_member_connect.models.expertise import Expertise
from mensa_member_connect.models.industry import Industry
from mensa_member_connect.models.local_group import LocalGroup


class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "first_name",
        "last_name",
        "email",
        "member_id",
        "role",
        "status",
    )


class AdminActionAdmin(admin.ModelAdmin):
    list_display = ("id", "admin_username", "target_username", "action", "created_at")

    def admin_username(self, obj):
        return obj.admin.username

    admin_username.admin_order_field = "admin__username"  # allows column sorting
    admin_username.short_description = "Admin User"

    def target_username(self, obj):
        return obj.target_user.username

    target_username.admin_order_field = "target_user__username"
    target_username.short_description = "Target User"


class ConnectionRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "seeker_username", "expert_username", "created_at")

    def seeker_username(self, obj):
        return obj.seeker.username

    seeker_username.admin_order_field = "seeker__username"
    seeker_username.short_description = "Seeker"

    def expert_username(self, obj):
        return obj.expert.user.username

    expert_username.admin_order_field = "expert__user__username"
    expert_username.short_description = "Expert"


class ExpertiseAdmin(admin.ModelAdmin):
    list_display = ("id", "expert_username", "what_offering")

    def expert_username(self, obj):
        if obj.expert and obj.expert.user:
            return obj.expert.user.username
        return "-"  # fallback if expert or user is missing

    expert_username.admin_order_field = "expert__user__username"
    expert_username.short_description = "Expert"


class IndustryAdmin(admin.ModelAdmin):
    list_display = ("id", "industry_name", "industry_description")


class LocalGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "group_name", "city", "state")


# Register models with default admin
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(AdminAction, AdminActionAdmin)
admin.site.register(ConnectionRequest, ConnectionRequestAdmin)
admin.site.register(Expertise, ExpertiseAdmin)
admin.site.register(Industry, IndustryAdmin)
admin.site.register(LocalGroup, LocalGroupAdmin)
