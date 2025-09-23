from django.conf import settings
from django.db import models
from mensa_member_connect.models.expert import Expert


class ConnectionRequest(models.Model):
    seeker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,  # consider adding blank=True if you want it optional in forms
    )
    expert = models.ForeignKey(
        Expert,
        on_delete=models.CASCADE,
        null=True,  # same here
    )
    message = models.TextField(blank=True, null=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
