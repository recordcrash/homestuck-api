from django.contrib import admin

from comic.models import Page


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('short_id', 'name', 'number', 'act', 'comic')
    search_fields = ('short_id', 'name', 'comic__name', 'act__name')
    ordering = ('short_id', )
    autocomplete_fields = ('act', 'comic')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('act', 'comic')
