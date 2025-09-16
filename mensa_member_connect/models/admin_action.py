from datetime import datetime
from django.conf import settings
from django.db import models


class AdminAction(models.Model):
    admin_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="admin_actions",
    )
    target_user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="targeted_actions",
    )
    action = models.CharField(max_length=128, default="")
    created_at = models.DateTimeField(default=datetime.now)
