from django.core.management.base import BaseCommand

from base.models import Artist, Link, Tag, Media, MediaArtist, Commentary, File, Art
from comic.models import Location, Character, Act, Page, Comic
from music.models import Group, Album, Track, TrackArtist, TrackAlbum, TrackReference, TrackMedia


# Usage: python manage.py delete_hsmusic_yaml_data
class Command(BaseCommand):
    help = 'Deletes all the data created by the import_hsmusic_yaml command. Useful for testing.'

    def handle(self, *args, **options):
        # Delete all imported models
        # or in loop form:
        for model in [TrackMedia, TrackReference, TrackAlbum, TrackArtist, Track, Album, Group, MediaArtist, Media,
                      Link, Tag, Artist, Location, Character, Act, Page, Comic, Commentary, File, Art]:
            model.objects.all().delete()
