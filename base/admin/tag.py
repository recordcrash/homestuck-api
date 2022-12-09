from django.contrib import admin

from base.models import Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('short_id', 'name', 'color')
    search_fields = ('short_id', 'name')
    ordering = ('short_id', )
