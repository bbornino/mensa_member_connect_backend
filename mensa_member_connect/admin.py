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
        "first_name",
        "last_name",
        "email",
        "member_id",
        "role",
        "status",
    )


class AdminActionAdmin(admin.ModelAdmin):
    list_display = ("id", "admin_email", "target_email", "action", "created_at")

    def admin_email(self, obj):
        return obj.admin.email

    admin_email.admin_order_field = "admin__email"
    admin_email.short_description = "Admin Email"

    def target_email(self, obj):
        return obj.target_user.email

    target_email.admin_order_field = "target_user__email"
    target_email.short_description = "Target Email"


class ConnectionRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "seeker_email", "expert_email", "created_at")

    def seeker_email(self, obj):
        return obj.seeker.email

    seeker_email.admin_order_field = "seeker__email"
    seeker_email.short_description = "Seeker"

    def expert_email(self, obj):
        return obj.expert.user.email

    expert_email.admin_order_field = "expert__user__email"
    expert_email.short_description = "Expert"


class ExpertiseAdmin(admin.ModelAdmin):
    list_display = ("id", "expert_email", "what_offering")

    def expert_email(self, obj):
        return getattr(getattr(obj.expert, "user", None), "email", "-")

    expert_email.admin_order_field = "expert__user__username"
    expert_email.short_description = "Expert"


class IndustryAdmin(admin.ModelAdmin):
    list_display = ("id", "industry_name", "industry_description")


class LocalGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "group_name", "group_number")


# Register models with default admin
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(AdminAction, AdminActionAdmin)
admin.site.register(ConnectionRequest, ConnectionRequestAdmin)
admin.site.register(Expertise, ExpertiseAdmin)
admin.site.register(Industry, IndustryAdmin)
admin.site.register(LocalGroup, LocalGroupAdmin)
