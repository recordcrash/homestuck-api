from colorfield.fields import ColorField
from django.db import models

from base.helpers.models.short_id_model import ShortIdModel


class GroupType(models.TextChoices):
    OFFICIAL = 'official', 'Official'
    FANS = 'fans', 'Fans'
    NONMSPA = 'non-mspa', 'Non-MSPA'


class Group(ShortIdModel):
    name = models.CharField(max_length=128, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    color = ColorField()
    image = models.ImageField(blank=True, null=True, upload_to='groups/')
    type = models.CharField(max_length=30, choices=GroupType.choices, blank=False, null=False,
                            default=GroupType.FANS)

    urls = models.ManyToManyField('base.Link', blank=True)

    def __str__(self):
        return self.name
