from django.db import models


class TrackMedia(models.Model):
    class Meta:
        ordering = ['position']
        unique_together = ('track', 'media')

    track = models.ForeignKey('music.Track', blank=False, null=False, on_delete=models.CASCADE)
    media = models.ForeignKey('base.Media', blank=False, null=False, on_delete=models.CASCADE)
    position = models.PositiveSmallIntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.track.name} - {self.media.name}'
