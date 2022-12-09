from django.db import models


class ShortIdModel(models.Model):
    short_id = models.CharField(max_length=256, unique=True, blank=False, null=False)

    class Meta:
        abstract = True
