from django.contrib import admin

from music.models import TrackAlbum


@admin.register(TrackAlbum)
class TrackAlbumAdmin(admin.ModelAdmin):
    list_display = ('track', 'album', 'position', 'alias', 'track_art',)
    search_fields = ('alias', 'track__name', 'album__name')
    autocomplete_fields = ('track', 'album', 'track_art')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('track', 'album', 'track_art')
