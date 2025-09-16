from datetime import datetime
from django.conf import settings
from django.db import models
from mensa_member_connect.models.expert import Expert


class ConnectionRequest(models.Model):
    seeker_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
    )
    expert_id = models.ForeignKey(
        Expert,
        on_delete=models.CASCADE,
        null=True,
    )
    message = models.TextField(default="", blank=True, null=True)
    created_at = models.DateTimeField(default=datetime.now)
