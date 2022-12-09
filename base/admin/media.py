from django.contrib import admin

from base.models import Media


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('short_id', 'name', 'color', 'date', 'image', 'page')
    search_fields = ('short_id', 'name')
    autocomplete_fields = ('page', 'urls', 'commentary')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('page')
