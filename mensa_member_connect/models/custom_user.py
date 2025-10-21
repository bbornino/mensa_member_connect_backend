from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from phonenumber_field.modelfields import PhoneNumberField
from mensa_member_connect.models.local_group import LocalGroup
from mensa_member_connect.models.industry import Industry


class CustomUser(AbstractUser):
    member_id = models.IntegerField(null=True, blank=True)
    city = models.CharField(max_length=48, blank=True, null=True)
    state = models.CharField(max_length=24, blank=True, null=True)
    phone = PhoneNumberField(blank=True, null=True)
    role = models.CharField(max_length=16, default="member")  # sensible default
    status = models.CharField(max_length=24, default="active")  # sensible default

    occupation = models.CharField(max_length=128, default="")
    industry = models.ForeignKey(
        Industry,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="user_experts",
    )
    background = models.TextField(default="", blank=True, null=True)
    # photo = models.CharField(max_length=128, default='')      # TODO: Will eventually add when implementation is determined
    availability_status = models.CharField(max_length=32, default="")
    show_contact_info = models.BooleanField(default=False)

    local_group = models.ForeignKey(
        LocalGroup,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
