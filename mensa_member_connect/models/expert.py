from django.conf import settings
from django.db import models
from mensa_member_connect.models.industry import Industry


class Expert(models.Model):
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
    )
    occupation = models.CharField(max_length=128, default="")
    industry_id = models.ForeignKey(
        Industry,
        on_delete=models.CASCADE,
        null=True,
    )
    background = models.TextField(default="", blank=True, null=True)
    # photo = models.CharField(max_length=128, default='')      # TODO: Will eventually add when implementation is determined
    availability_status = models.CharField(max_length=32, default="")
    show_contact_info = models.BooleanField(default=False)
