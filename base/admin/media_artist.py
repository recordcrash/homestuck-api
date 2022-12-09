from django.contrib import admin

from base.models import MediaArtist


@admin.register(MediaArtist)
class MediaArtistAdmin(admin.ModelAdmin):
    list_display = ('media', 'artist', 'artist_type')
    search_fields = ('media__name', 'artist__name')
    autocomplete_fields = ('media', 'artist')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('media', 'artist')