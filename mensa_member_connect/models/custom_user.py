from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from phonenumber_field.modelfields import PhoneNumberField
from mensa_member_connect.models.local_group import LocalGroup


class CustomUser(AbstractUser):
    member_id = models.IntegerField()
    city = models.CharField(max_length=48)
    state = models.CharField(max_length=24)
    phone = PhoneNumberField(blank=True, null=True)
    role = models.CharField(max_length=16)
    status = models.CharField(max_length=24)
    local_group_id = models.ForeignKey(
        LocalGroup,
        on_delete=models.CASCADE,
        null=True,
    )
