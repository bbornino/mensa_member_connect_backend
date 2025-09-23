from django.db import models


class LocalGroup(models.Model):
    group_name = models.CharField(max_length=128, default="")
    city = models.CharField(max_length=48, default="")
    state = models.CharField(max_length=16, default="")

    def __str__(self):
        return self.group_name
