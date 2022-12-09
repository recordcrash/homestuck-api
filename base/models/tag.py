from colorfield.fields import ColorField
from django.db import models

from base.helpers.models.short_id_model import ShortIdModel


class Tag(ShortIdModel):
    name = models.CharField(max_length=128, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    color = ColorField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
