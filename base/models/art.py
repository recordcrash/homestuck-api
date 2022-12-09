from django.db import models

from base.helpers.models.short_id_model import ShortIdModel


class Art(ShortIdModel):
    image = models.ImageField(max_length=512, upload_to='arts/', blank=False, null=False)
    notes = models.TextField(blank=True, null=True)
    characters = models.ManyToManyField('comic.Character', blank=True, related_name='art_characters')
    locations = models.ManyToManyField('comic.Location', blank=True, related_name='art_locations')
    artist = models.ForeignKey('base.Artist', blank=True, null=True, on_delete=models.SET_NULL)
    commentary = models.ManyToManyField('base.Commentary', blank=True, related_name='arts')

    def __str__(self):
        return self.short_id
