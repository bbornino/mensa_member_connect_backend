from django.db import models
from mensa_member_connect.models.expert import Expert


class Expertise(models.Model):
    expert_id = models.ForeignKey(
        Expert,
        on_delete=models.CASCADE,
        null=True,
    )
    what_offering = models.TextField(blank=True, null=True)
    who_would_benefit = models.TextField(blank=True, null=True)
    why_choose_you = models.TextField(blank=True, null=True)
    skills_not_offered = models.TextField(blank=True, null=True)
