from django.contrib import admin

from base.models import Commentary


@admin.register(Commentary)
class CommentaryAdmin(admin.ModelAdmin):
    list_display = ('short_id', 'text', 'artist')
    search_fields = ('short_id', 'text')
    autocomplete_fields = ('artist',)
