from django.db import models

from base.helpers.models.short_id_model import ShortIdModel


class Act(ShortIdModel):
    name = models.CharField(max_length=128, blank=False, null=False)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    comic = models.ForeignKey('comic.Comic', blank=False, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
