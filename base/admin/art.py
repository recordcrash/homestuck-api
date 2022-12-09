from django.contrib import admin

from base.models import Art


@admin.register(Art)
class ArtAdmin(admin.ModelAdmin):
    list_display = ('short_id', 'image')
    search_fields = ('short_id', 'artist__name')
    autocomplete_fields = ('characters', 'locations', 'artist', 'commentary')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('artist')
