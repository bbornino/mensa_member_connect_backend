from django.db import models

class Industry(models.Model):
    industry_name = models.CharField(max_length=128, default='')
    industry_description = models.CharField(max_length=48, default='')

