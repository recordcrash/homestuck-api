from django.db import models

from base.helpers.models.short_id_model import ShortIdModel


class File(ShortIdModel):
    name = models.CharField(max_length=256, blank=False, null=False)
    file = models.FileField(upload_to='files/', blank=False, null=False)
    notes = models.TextField(blank=True, null=True)
    artist = models.ForeignKey('base.Artist', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.short_id
