from django.contrib import admin

from music.models import TrackArtist


@admin.register(TrackArtist)
class TrackArtistAdmin(admin.ModelAdmin):
    list_display = ('track', 'artist', 'artist_type')
    search_fields = ('alias', 'track__name', 'artist__name')
    autocomplete_fields = ('track', 'artist')
    list_filter = ('artist_type',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('track', 'artist')
