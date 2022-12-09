from django.db import models

from base.helpers.models.short_id_model import ShortIdModel


class Commentary(ShortIdModel):
    text = models.TextField(blank=False, null=False)
    artist = models.ForeignKey('base.Artist', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.short_id
