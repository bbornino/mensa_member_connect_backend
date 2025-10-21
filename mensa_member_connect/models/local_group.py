from django.db import models
from django.core.validators import RegexValidator


class LocalGroup(models.Model):
    group_name = models.CharField(max_length=128, default="")
    group_number = models.CharField(
        max_length=3,
        unique=True,
        default="000",
        validators=[RegexValidator(r"^\d{3}$", "Enter a 3-digit number")],
    )

    def __str__(self):
        return str(self.group_name)
