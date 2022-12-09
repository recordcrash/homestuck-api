from django_better_admin_arrayfield.models.fields import ArrayField
from django.db import models

from base.helpers.models.artist_type import ArtistType
from base.helpers.models.short_id_model import ShortIdModel


class Artist(ShortIdModel):
    name = models.CharField(max_length=128, blank=False, null=False)
    aliases = ArrayField(models.CharField(max_length=128), blank=True, null=True)
    artist_types = ArrayField(models.CharField(max_length=30, choices=ArtistType.choices, blank=False, null=False,
                                               default=[ArtistType.MUSICIAN]))
    urls = models.ManyToManyField('base.Link', blank=True)

    def __str__(self):
        return self.name
