from django.contrib import admin

from music.models import TrackMedia


@admin.register(TrackMedia)
class TrackMediaAdmin(admin.ModelAdmin):
    list_display = ('track', 'media', 'position')
    search_fields = ('track__name', 'media__name')
    autocomplete_fields = ('track', 'media')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('track', 'media')
