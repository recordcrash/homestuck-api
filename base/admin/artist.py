from django.contrib import admin

from base.models import Artist
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin, DynamicArrayMixin):
    list_display = ('short_id', 'name', 'aliases', 'artist_types')
    search_fields = ('short_id', 'name')
    ordering = ('short_id', )
    autocomplete_fields = ('urls', )
