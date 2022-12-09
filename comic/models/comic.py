from colorfield.fields import ColorField
from django.db import models

from base.helpers.models.short_id_model import ShortIdModel


class Comic(ShortIdModel):
    name = models.CharField(max_length=128, blank=False, null=False)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    color = ColorField()
    urls = models.ManyToManyField('base.Link', blank=True)
    image = models.ImageField(max_length=512, upload_to='comics/', blank=True, null=True)

    def __str__(self):
        return self.name
