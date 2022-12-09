from django.db import models

from base.helpers.models.short_id_model import ShortIdModel


class Track(ShortIdModel):
    name = models.CharField(max_length=512, blank=False, null=False)
    duration = models.DurationField(blank=True, null=True)
    lyrics = models.TextField(blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    characters = models.ManyToManyField('comic.Character', blank=True, related_name='track_characters')
    locations = models.ManyToManyField('comic.Location', blank=True, related_name='track_locations')
    urls = models.ManyToManyField('base.Link', blank=True)
    tags = models.ManyToManyField('base.Tag', blank=True)
    commentary = models.ManyToManyField('base.Commentary', blank=True)
    files = models.ManyToManyField('base.File', blank=True)

    def __str__(self):
        return self.name
