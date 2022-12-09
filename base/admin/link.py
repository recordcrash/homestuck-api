from django.contrib import admin

from base.models import Link


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('link', 'is_dead', 'link_type')
    list_filter = ('is_dead', 'link_type')
    search_fields = ('link', )
