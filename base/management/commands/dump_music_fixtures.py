from django.core.management.base import BaseCommand

from django.core import management


# Usage: python manage.py dump_music_fixtures
class Command(BaseCommand):
    help = 'Uses other manage.py commands to dump all the fixtures to its expected filenames'
    model_tuples = [
        ('base.link', '0_base_0_link'),
        ('base.tag', '0_base_0_tag'),
        ('base.artist', '0_base_1_artist'),
        ('base.commentary', '0_base_2_commentary'),
        ('base.file', '0_base_2_file'),
        ('base.media', '0_base_3_media'),
        ('base.mediaartist', '0_base_4_media_artist'),
        ('comic.character', '1_comic_0_character'),
        ('comic.comic', '1_comic_0_comic'),
        ('comic.location', '1_comic_0_location'),
        ('comic.act', '1_comic_1_act'),
        ('comic.page', '1_comic_2_page'),
        ('base.art', '2_base_0_art'),
        ('music.group', '2_music_0_group'),
        ('music.track', '2_music_0_track'),
        ('music.album', '2_music_1_album'),
        ('music.trackartist', '2_music_1_track_artist'),
        ('music.trackmedia', '2_music_1_track_media'),
        ('music.trackreference', '2_music_1_track_reference'),
        ('music.trackalbum', '2_music_2_track_album'),
    ]

    def handle(self, *args, **options):
        for model, filename in self.model_tuples:
            self.stdout.write('Dumping {} to {}'.format(model, filename))
            management.call_command('dumpdata', model, indent=2, format='json', output=f'fixtures/{filename}.json')

