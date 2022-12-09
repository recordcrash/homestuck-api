from django.db import models

from base.helpers.models.artist_type import ArtistType


class MediaArtist(models.Model):
    class Meta:
        unique_together = ('media', 'artist')

    media = models.ForeignKey('base.Media', blank=False, null=False, on_delete=models.CASCADE)
    artist = models.ForeignKey('base.Artist', blank=False, null=False, on_delete=models.CASCADE)
    artist_type = models.CharField(max_length=30, choices=ArtistType.choices, blank=False, null=False,
                                   default=ArtistType.ARTIST)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.media.name + ' - ' + self.artist.name
