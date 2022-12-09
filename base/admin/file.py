from django.contrib import admin

from base.models import File


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('short_id', 'name', 'file', 'artist')
    search_fields = ('short_id', 'name', 'artist__name')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('artist')
