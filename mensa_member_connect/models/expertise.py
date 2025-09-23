from django.db import models
from mensa_member_connect.models.expert import Expert


class Expertise(models.Model):
    expert = models.ForeignKey(
        Expert,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="expertises",
    )
    what_offering = models.TextField(blank=True, null=True)
    who_would_benefit = models.TextField(blank=True, null=True)
    why_choose_you = models.TextField(blank=True, null=True)
    skills_not_offered = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.expert and self.expert.user:
            return f"Expertise of {self.expert.user.username}"
        return "Expertise (No Expert)"
