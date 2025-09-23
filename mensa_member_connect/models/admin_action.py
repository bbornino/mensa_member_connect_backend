from django.conf import settings
from django.db import models


class AdminAction(models.Model):
    # User who performed the action
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="admin_actions",
    )

    # User who is the target of the action
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="targeted_actions",
    )

    action = models.CharField(max_length=128, default="")

    # Automatically set when object is created, stored in UTC
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        admin_username = self.admin.username if self.admin else "Unknown"
        target_username = self.target_user.username if self.target_user else "Unknown"
        return f"{admin_username} → {target_username}: {self.action}"
