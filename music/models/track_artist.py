from django.db import models

from base.helpers.models.artist_type import ArtistType


class TrackArtist(models.Model):
    class Meta:
        unique_together = ('track', 'artist')

    track = models.ForeignKey('music.Track', blank=False, null=False, on_delete=models.CASCADE)
    artist = models.ForeignKey('base.Artist', blank=False, null=False, on_delete=models.CASCADE)
    artist_type = models.CharField(max_length=30, choices=ArtistType.choices, blank=False, null=False,
                                   default=ArtistType.MUSICIAN)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.track.name} - {self.artist.name}'
