from django_better_admin_arrayfield.models.fields import ArrayField
from django.db import models


class TrackReference(models.Model):
    class Meta:
        unique_together = ('referencing_track', 'referenced_track')

    referencing_track = models.ForeignKey('music.Track', blank=False, null=False, on_delete=models.CASCADE,
                                          related_name='references_as_referencing_track')
    referenced_track = models.ForeignKey('music.Track', blank=False, null=False, on_delete=models.CASCADE,
                                         related_name='references_as_referenced_track')
    timestamps = ArrayField(models.DurationField(), blank=True, null=True,
                            help_text='Timestamps in the referencing track. Pairs of [[HH:]MM:]ss timestamps.')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.referenced_track.name} (referenced by {self.referencing_track.name})'
