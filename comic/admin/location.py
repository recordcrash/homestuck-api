from django.contrib import admin

from comic.models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('short_id', 'name', 'color', 'image')
    search_fields = ('short_id', 'name')
    ordering = ('short_id', )
