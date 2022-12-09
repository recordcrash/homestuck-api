from django.contrib import admin
from django.db import models
from django.forms import Textarea

from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
from music.models import Track, TrackAlbum, TrackArtist, TrackMedia, TrackReference


class TrackArtistInline(admin.TabularInline):
    model = TrackArtist
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    autocomplete_fields = ['artist']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('track', 'artist')


class TrackAlbumInline(admin.TabularInline):
    model = TrackAlbum
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    autocomplete_fields = ['album', 'track_art']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('track', 'album')


class TrackMediaInline(admin.TabularInline):
    model = TrackMedia
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    autocomplete_fields = ['media']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('track', 'media')


class TrackReferenceReferencingInline(admin.TabularInline, DynamicArrayMixin):
    model = TrackReference
    verbose_name = 'Tracks referenced by this track'
    verbose_name_plural = 'Tracks referenced by this track'
    fk_name = 'referencing_track'
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }

    autocomplete_fields = ['referenced_track']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('referencing_track', 'referenced_track')


class TrackReferenceReferencedInline(admin.TabularInline, DynamicArrayMixin):
    model = TrackReference
    verbose_name = 'Tracks that reference this track'
    verbose_name_plural = 'Tracks that reference this track'
    fk_name = 'referenced_track'
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }

    autocomplete_fields = ['referencing_track']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('referencing_track', 'referenced_track')


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('id', 'short_id', 'name', 'release_date', 'duration')
    search_fields = ('short_id', 'name')
    autocomplete_fields = ('characters', 'locations', 'urls', 'tags', 'commentary', 'files')

    inlines = (TrackAlbumInline, TrackMediaInline, TrackArtistInline, TrackReferenceReferencingInline,
               TrackReferenceReferencedInline)

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }

    # queryset for the inline
    def get_queryset(self, request):
        return super().get_queryset(request) \
            .prefetch_related('characters', 'locations', 'urls', 'tags', 'commentary', 'files')
