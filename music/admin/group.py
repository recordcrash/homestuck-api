from django.contrib import admin

from music.models import Group


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('short_id', 'name', 'color', 'image', 'type')
    search_fields = ('short_id', 'name')
    autocomplete_fields = ('urls',)
