from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, UserManager
from typing import Optional
from phonenumber_field.modelfields import PhoneNumberField
from mensa_member_connect.models.local_group import LocalGroup
from mensa_member_connect.models.industry import Industry


class CustomUserManager(UserManager["CustomUser"]):
    def create_user(self, email: str, password: Optional[str] = None, **extra_fields):
        if not email:
            raise ValueError("Email must be provided")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, password: Optional[str] = None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):

    username = None  # Remove username field entirely
    email = models.EmailField(unique=True)  # Make email the main identifier
    USERNAME_FIELD = "email"  # authenticate with email instead of username.
    REQUIRED_FIELDS = []  # prevents Django from prompting for a username

    objects = CustomUserManager()

    member_id = models.IntegerField(null=True, blank=True)
    city = models.CharField(max_length=48, blank=True, null=True)
    state = models.CharField(max_length=24, blank=True, null=True)
    phone = PhoneNumberField(blank=True, null=True)
    role = models.CharField(max_length=16, default="member")
    status = models.CharField(max_length=24, default="pending")

    occupation = models.CharField(max_length=128, default="", blank=True)
    industry = models.ForeignKey(
        Industry,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="user_experts",
    )
    background = models.TextField(default="", blank=True, null=True)
    profile_photo = models.BinaryField(null=True, blank=True)
    availability_status = models.CharField(max_length=32, default="")
    show_contact_info = models.BooleanField(default=False)

    local_group = models.ForeignKey(
        LocalGroup,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
