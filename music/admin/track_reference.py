from django.contrib import admin

from music.models import TrackReference
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin

@admin.register(TrackReference)
class TrackReferenceAdmin(admin.ModelAdmin, DynamicArrayMixin):
    list_display = ('referencing_track', 'referenced_track')
    search_fields = ('referencing_track__name', 'referenced_track__name')
    autocomplete_fields = ('referencing_track', 'referenced_track')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('referencing_track', 'referenced_track', )
