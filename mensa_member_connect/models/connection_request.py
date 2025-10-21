from django.conf import settings
from django.db import models


class ConnectionRequest(models.Model):
    seeker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,  # consider adding blank=True if you want it optional in forms
        related_name="connection_requests_sent",
    )
    expert = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,  # same here
        related_name="connection_requests_received",
    )
    message = models.TextField(blank=True, null=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
