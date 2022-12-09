from django.db import models

from base.helpers.models.short_id_model import ShortIdModel


class Page(ShortIdModel):
    name = models.CharField(max_length=256, blank=False, null=False)
    number = models.PositiveSmallIntegerField(blank=True, null=True)
    act = models.ForeignKey('comic.Act', blank=True, null=True, on_delete=models.SET_NULL)
    comic = models.ForeignKey('comic.Comic', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name if self.number is None else f'{self.number} - {self.name}'
