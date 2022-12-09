from colorfield.fields import ColorField
from django.db import models

from base.helpers.models.short_id_model import ShortIdModel


class Media(ShortIdModel):
    name = models.CharField(max_length=512, blank=False, null=False)
    color = ColorField()
    date = models.DateField(blank=True, null=True)
    image = models.ImageField(max_length=512, upload_to='medias/', blank=True, null=True)
    page = models.ForeignKey('comic.Page', blank=True, null=True, on_delete=models.SET_NULL)
    urls = models.ManyToManyField('base.Link', blank=True)
    commentary = models.ManyToManyField('base.Commentary', blank=True, related_name='medias')

    def __str__(self):
        return self.name
