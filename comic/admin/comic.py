from django.contrib import admin

from comic.models import Comic


@admin.register(Comic)
class ComicAdmin(admin.ModelAdmin):
    list_display = ('short_id', 'name', 'start_date', 'end_date', 'color', 'image')
    search_fields = ('short_id', 'name')
    ordering = ('short_id',)
    autocomplete_fields = ('urls',)
