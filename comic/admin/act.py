from django.contrib import admin

from comic.models import Act


@admin.register(Act)
class ActAdmin(admin.ModelAdmin):
    list_display = ('short_id', 'name', 'start_date', 'end_date', 'comic')
    search_fields = ('short_id', 'name')
    ordering = ('short_id',)
    autocomplete_fields = ('comic',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('comic', )
