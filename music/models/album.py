from colorfield.fields import ColorField
from django.db import models

from base.helpers.models.short_id_model import ShortIdModel


class Album(ShortIdModel):
    name = models.CharField(max_length=256, blank=False, null=False)
    release_date = models.DateField(blank=True, null=True)
    color = ColorField()
    notes = models.TextField(blank=True, null=True)

    cover_art = models.ForeignKey('base.Art', blank=True, null=True, on_delete=models.SET_NULL)
    groups = models.ManyToManyField('music.Group', blank=True, related_name='albums')
    urls = models.ManyToManyField('base.Link', blank=True)
    commentary = models.ManyToManyField('base.Commentary', blank=True, related_name='albums')
    files = models.ManyToManyField('base.File', blank=True, related_name='albums')

    def __str__(self):
        return self.name
