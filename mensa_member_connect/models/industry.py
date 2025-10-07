from django.db import models


class Industry(models.Model):
    industry_name = models.CharField(max_length=128, default="")
    industry_description = models.CharField(max_length=512, default="")

    def __str__(self):
        return str(self.industry_name)
