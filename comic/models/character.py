from colorfield.fields import ColorField
from django.db import models

from base.helpers.models.short_id_model import ShortIdModel


class Character(ShortIdModel):
    name = models.CharField(max_length=128, blank=False, null=False)
    color = ColorField()
    image = models.ImageField(max_length=512, upload_to='characters/', blank=True, null=True)

    def __str__(self):
        return self.name
