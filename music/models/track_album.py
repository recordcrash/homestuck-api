from django.db import models


class TrackAlbum(models.Model):
    class Meta:
        ordering = ['position']
        unique_together = ('track', 'album')

    track = models.ForeignKey('music.Track', blank=False, null=False, on_delete=models.CASCADE)
    album = models.ForeignKey('music.Album', blank=False, null=False, on_delete=models.CASCADE)
    track_art = models.ForeignKey('base.Art', blank=True, null=True, on_delete=models.SET_NULL)
    alias = models.CharField(max_length=512, blank=True, null=True)
    position = models.PositiveSmallIntegerField(blank=False, null=False)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.track.name} - {self.album.name}'
