from django.contrib import admin
from django.db import models
from django.forms import Textarea

from music.models import Album, TrackAlbum


class TrackAlbumInlineAdmin(admin.TabularInline):
    model = TrackAlbum
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    autocomplete_fields = ['album', 'track_art']
    # change order of fields so position goes first
    fields = ['position', 'alias', 'track_art', 'notes']


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('id', 'short_id', 'name', 'release_date', 'color', 'cover_art')
    search_fields = ('short_id', 'name')
    autocomplete_fields = ('groups', 'urls', 'commentary', 'files')
    inlines = [TrackAlbumInlineAdmin]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cover_art')
