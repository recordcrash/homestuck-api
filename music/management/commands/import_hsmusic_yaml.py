import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timedelta, date

import yaml
from django.core.files import File as DjangoFile
from django.core.files.temp import NamedTemporaryFile
from django.core.management.base import BaseCommand
from django.db import transaction

from base.helpers.models.artist_type import ArtistType
from base.models import Artist, Link, Tag, Media, MediaArtist, Commentary, File, Art
from comic.models import Location, Character, Act, Page, Comic
from music.models import Group, Album, Track, TrackArtist, TrackAlbum, TrackReference, TrackMedia
from music.models.group import GroupType


# Usage: python manage.py import_hsmusic_yaml --check-links True --media-folder hsmusic-media --data-folder hsmusic-data
# All parameters optional
# Caveats: Do not run this once the database is populated, you'll get a bunch of garbage in the media folder when files
# are reuploaded and the filenames are taken. Run the delete hsmusic yaml data task.
class Command(BaseCommand):
    help = 'Import songs from YAML files. Use --check-links parameter so links are checked for 404, ' \
           '--media-folder and --data-folder to specify (relative to base) folder locations'

    # Helper dicts that use the three formats in the yamls to help you get a database object
    # Format short_id: object / model:short_id: object / name: object
    # These dicts will build up as the command progresses
    _characters_dict = {}
    _locations_dict = {}
    _groups_dict = {}
    _artists_dict = {}
    _tags_dict = {}
    _tracks_dict = {}
    _albums_dict = {}
    _media_dict = {}
    _files_dict = {}
    _arts_dict = {}
    # These dicts don't have a short_id, so we have to use the name
    _links_dict = {}
    # This is a bunch of files for an album_id
    _album_files_dict = {}
    # Other global variables
    _wiki_data_folder = None
    _wiki_media_folder = None
    _check_links = False

    def add_arguments(self, parser):
        parser.add_argument('--check-links', default=False, help='Check links for 404')
        parser.add_argument('--media-folder', default='hsmusic-media', help='Folder where media is stored')
        parser.add_argument('--data-folder', default='hsmusic-data', help='Folder where data is stored')

    def handle(self, *args, **options):
        check_links = options['check_links']
        media_folder = options['media_folder']
        data_folder = options['data_folder']
        self._check_links = check_links
        # Thank you, DJ Sai Tae, the following is needed just to process asian characters in print statements
        sys.stdin.reconfigure(encoding='utf-8')
        sys.stdout.reconfigure(encoding='utf-8')
        # Get data folder and media folder options, with a default
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self._wiki_data_folder = os.path.join(base_dir, data_folder)
        self._wiki_media_folder = os.path.join(base_dir, media_folder)

        # Transaction.atomic() ensures that either the entire process works, or nothing is created in the DB
        with transaction.atomic():
            self._import_files()
            self._import_characters_locations_and_tags()
            self._import_groups()
            self._import_artists()
            self._import_albums_and_tracks()
            self._import_media_and_comic_data()

    def _import_files(self):
        # All the files will be imported in advance, and will be easily findable through short_ids when the
        # rest of entities are being imported, and fetched from the dicts if they exist
        files_to_create = []
        arts_to_create = []
        album_additional_folder = os.path.join(self._wiki_media_folder, f'album-additional')
        temporary_file_folder = '/var/tmp'
        # Handle album additional files (banners, commentary booklets...)
        for album_id in os.listdir(album_additional_folder):
            print(f'Processing album additional files for {album_id}...')
            for file in os.listdir(os.path.join(album_additional_folder, album_id)):
                print(f'Processing file: {file} for album {album_id}')
                # Remove extensions
                file_name = os.path.splitext(file)[0]

                # Must use temporary files to avoid SuspiciousFileOperation error
                lf = NamedTemporaryFile(dir=temporary_file_folder)
                with open(os.path.join(album_additional_folder, album_id, file), 'rb') as f:
                    lf.write(f.read())
                    file_to_create = File(
                        short_id=f'{album_id}_{file_name}', name=file, file=DjangoFile(lf, name=file)
                    )
                if album_id not in self._album_files_dict:
                    self._album_files_dict[album_id] = []
                self._album_files_dict[album_id].append(file_to_create)
                files_to_create.append(file_to_create)
        # Handle album and track art
        album_art_folder = os.path.join(self._wiki_media_folder, f'album-art')
        for album_id in os.listdir(album_art_folder):
            if not os.path.isdir(os.path.join(album_art_folder, album_id)):
                continue
            print(f'Processing album art: {album_id}')
            for file in os.listdir(os.path.join(album_art_folder, album_id)):
                file_name = os.path.splitext(file)[0]
                print(f'Processing file: {file} for album {album_id}')
                skipped_file_names = ['banner.png', 'strife.png']
                if file in skipped_file_names:
                    print(f'Skipping file: {file} for album {album_id}')
                    continue
                lf = NamedTemporaryFile(dir=temporary_file_folder)
                with open(os.path.join(album_art_folder, album_id, file), 'rb') as f:
                    lf.write(f.read())
                    if file_name == 'cover':
                        album_art = Art(short_id=album_id, image=DjangoFile(lf, name=file))
                        arts_to_create.append(album_art)
                    elif file_name == 'banner':
                        album_banner = Art(short_id=f'{album_id}_banner', image=DjangoFile(lf, name=file))
                        arts_to_create.append(album_banner)
                    elif file_name == 'bg':
                        album_bg = Art(short_id=f'{album_id}_bg', image=DjangoFile(lf, name=file))
                        arts_to_create.append(album_bg)
                    else:
                        # Track art
                        arts_to_create.append(
                            Art(short_id=f"{album_id}-{file_name}", image=DjangoFile(lf, name=file))
                        )
        # Handle flash/game files
        flash_folder = os.path.join(self._wiki_media_folder, f'flash-art')
        for file in os.listdir(flash_folder):
            print(f'Processing flash file: {file}')
            # Remove when hsmusic-media is fixed
            skipped_file_names = ['psych-ch1.png', 'psych-ch2.png', 'psych-ch3.png', 'psych-ch4.png']
            if file in skipped_file_names:
                print(f'Skipping file {file}')
                continue
            file_name = os.path.splitext(file)[0]
            lf = NamedTemporaryFile(dir=temporary_file_folder)
            with open(os.path.join(flash_folder, file), 'rb') as f:
                lf.write(f.read())
                files_to_create.append(File(
                    short_id=file_name, name=file, file=DjangoFile(lf, name=file)
                ))
        # Handle misc files (just upload for now)
        misc_folder = os.path.join(self._wiki_media_folder, f'misc')
        for file in os.listdir(misc_folder):
            if os.path.isdir(os.path.join(misc_folder, file)):
                continue
            print(f'Processing misc file: {file}')
            file_name = os.path.splitext(file)[0]
            lf = NamedTemporaryFile(dir=temporary_file_folder)
            with open(os.path.join(misc_folder, file), 'rb') as f:
                lf.write(f.read())
                files_to_create.append(File(
                    short_id=f"misc_{file_name}", name=file, file=DjangoFile(lf, name=file)
                ))

        print('Creating files (this might take a couple minutes)...')
        files = File.objects.bulk_create(files_to_create)
        arts = Art.objects.bulk_create(arts_to_create)
        self._arts_dict = {
            art.short_id: art for art in arts
        }
        self._files_dict = {
            file.short_id: file for file in files
        }
        print(f'Created {len(files)} files and {len(arts)} arts')

    def _import_media_and_comic_data(self):
        # Jesus christ, the flashes.yaml text includes even games, and we have no
        # way of distinguishing them. This one is going to need fixing by hand afterwards.
        flashes = self._load_yaml(self._wiki_data_folder, 'flashes.yaml')
        # Process links first
        link_list = [
            link
            for flash in flashes
            for link in flash.get('URLs', [])
        ]
        self._import_links(link_list)
        pages_to_create = []
        acts_to_create = []
        media_to_create = []
        media_links_to_create = []
        track_media_to_create = []
        media_artists_to_create = []
        current_act = None
        homestuck = Comic.objects.create(short_id='homestuck', name='Homestuck', start_date=date(2009, 4, 13),
                                         end_date=date(2016, 10, 25), color='00FF00')
        for flash in flashes:
            act = flash.get('Act', None)
            if act is not None:
                anchor = flash.get('Anchor')
                short_id = anchor if anchor is not None else self._normalize_utf(act)
                # Manual exception because yaml is just wrong
                if short_id == 'a2' and 'Intermission' in act:
                    short_id = 'i2'
                if short_id == 'a6a2' and 'Intermission' in act:
                    short_id = 'a6i2'
                current_act = Act(short_id=short_id, name=act, comic=homestuck)
                acts_to_create.append(current_act)
            else:
                page = flash.get('Page')
                if page is not None:
                    flash_name = flash.get('Flash')
                    featured_tracks = [
                        self._tracks_dict.get(track)
                        for track in flash.get('Featured Tracks', [])
                    ]
                    short_id = flash.get('Directory', flash.get('Page'))
                    try:
                        page_number = int(page)
                    except ValueError:
                        page_number = None
                    page = Page(short_id=short_id, name=flash_name, act=current_act, number=page_number,
                                comic=homestuck)
                    media = Media(short_id=short_id, name=flash_name, page=page,
                                  date=self._yaml_date_to_date(flash.get('Date')))
                    self._media_dict[short_id] = media
                    self._media_dict[flash_name] = media
                    self._media_dict[f'flash:{short_id}'] = media
                    pages_to_create.append(page)
                    media_to_create.append(media)
                    media_links_to_create.extend([
                        Media.urls.through(media=media, link=self._links_dict.get(link))
                        for link in flash.get('URLs', [])
                    ])
                    track_media_to_create.extend([
                        TrackMedia(track=track, media=media, position=index)
                        for index, track in enumerate(featured_tracks)
                    ])
                    artist_tuples = self._get_artist_tuples(flash.get('Contributors', []),
                                                            default_role=ArtistType.ARTIST)
                    media_artists_to_create.extend([
                        MediaArtist(artist=artist, media=media,
                                    artist_type=artist_type, notes=artist_roles)
                        for (artist, artist_type, artist_roles) in artist_tuples
                    ])
        # We can now create everything
        # Print all acts and attributes
        for act in acts_to_create:
            print(f'Added act: {act.name} (short_id={act.short_id})')
        Act.objects.bulk_create(acts_to_create)
        Page.objects.bulk_create(pages_to_create)
        Media.objects.bulk_create(media_to_create)
        Media.urls.through.objects.bulk_create(media_links_to_create)
        TrackMedia.objects.bulk_create(track_media_to_create)
        MediaArtist.objects.bulk_create(media_artists_to_create)

    def _process_media_contributor(self, media, contributor_string):
        if contributor_string is not None:
            # A contributor string is of the format "Artist Name (Role, Role 2..) or Artist Name without parentheses"
            # We need to reliably get the artist name no matter the format
            string_split = contributor_string.split('(')
            if len(string_split) == 1:
                artist_name = string_split[0].strip()
                MediaArtist.objects.create(artist=self._artists_dict.get(artist_name), media=media,
                                           artist_type=ArtistType.ARTIST)
            else:
                artist_name = string_split[0].strip()
                artist_types_string = string_split[1].strip(')').strip()
                # Split into commas
                artist_type_string = artist_types_string.split(',')
                # Process the first role to avoid spamming multiple art roles (if someone did
                # art and something else, we can add it manually later)
                MediaArtist.objects.create(
                    artist=self._artists_dict.get(artist_name), media=media,
                    artist_type=ArtistType.get_artist_type_from_string(artist_type_string[0])
                )
        else:
            return None

    def _import_albums_and_tracks(self):
        # Most sane variable naming scheme ever
        albums_path = os.path.join(self._wiki_data_folder, 'album')
        album_paths = os.listdir(albums_path)
        print(f'Processing {len(album_paths)} albums...')
        creation_dicts = []
        for album_path in album_paths:
            creation_dict = self._import_album(albums_path, album_path)
            if creation_dict is not None:
                creation_dicts.append(creation_dict)

        print(f'Creating {len(creation_dicts)} albums...')
        # First of all, sort the creation dicts based on the release date of the album
        date_year_3000 = date(3000, 1, 1)  # Make sure albums without a release date are last
        creation_dicts.sort(key=lambda x: x['album'].release_date or date_year_3000)
        # Now that everything is sorted, ids will canonically be sorted by album release date, making the first track
        # of the first album (Showtime Piano Refrain) the first track in the database
        Album.objects.bulk_create([creation_dict['album'] for creation_dict in creation_dicts])
        Commentary.objects.bulk_create([
            commentary
            for creation_dict in creation_dicts
            for commentary in creation_dict['commentaries']
        ])
        Album.urls.through.objects.bulk_create([
            album_url
            for creation_dict in creation_dicts
            for album_url in creation_dict['album_urls']
        ])
        Album.commentary.through.objects.bulk_create([
            album_commentary
            for creation_dict in creation_dicts
            for album_commentary in creation_dict['album_commentaries']
        ])
        Album.groups.through.objects.bulk_create([
            album_group
            for creation_dict in creation_dicts
            for album_group in creation_dict['album_groups']
        ])
        Album.files.through.objects.bulk_create([
            album_file
            for creation_dict in creation_dicts
            for album_file in creation_dict['album_files']
        ])
        Track.objects.bulk_create([
            track
            for creation_dict in creation_dicts
            for track in creation_dict['tracks']
        ])
        TrackAlbum.objects.bulk_create([
            track_album
            for creation_dict in creation_dicts
            for track_album in creation_dict['track_albums']
        ])
        TrackArtist.objects.bulk_create([
            track_artist
            for creation_dict in creation_dicts
            for track_artist in creation_dict['track_artists']
        ])
        Track.commentary.through.objects.bulk_create([
            track_commentary
            for creation_dict in creation_dicts
            for track_commentary in creation_dict['track_commentaries']
        ])
        Track.urls.through.objects.bulk_create([
            track_url
            for creation_dict in creation_dicts
            for track_url in creation_dict['track_urls']
        ])
        Track.locations.through.objects.bulk_create([
            location
            for creation_dict in creation_dicts
            for location in creation_dict['locations']
        ])
        Track.characters.through.objects.bulk_create([
            character
            for creation_dict in creation_dicts
            for character in creation_dict['characters']
        ])
        Track.tags.through.objects.bulk_create([
            tag
            for creation_dict in creation_dicts
            for tag in creation_dict['tags']
        ])

        for track in Track.objects.all():
            self._tracks_dict[f"track:{track.short_id}"] = track
            self._tracks_dict[track.short_id] = track
            self._tracks_dict[track.name] = track

        print('Processing albums a second time for references...')
        reference_creation_dicts = []
        for album_path in album_paths:
            print(f'Processing album {album_path} references...')
            creation_dict = self._import_album_references(albums_path, album_path)
            if creation_dict is not None:
                reference_creation_dicts.append(creation_dict)
        reference_creation_dicts.sort(key=lambda x: x['album'].release_date or date_year_3000)
        # We ignore the conflicts because the information is duplicated across albums
        TrackReference.objects.bulk_create([
            track_reference
            for creation_dict in reference_creation_dicts
            for track_reference in creation_dict['track_references']], ignore_conflicts=True
        )

    def _import_album(self, hsmusic_album_folder, album_path) -> dict | None:
        album_data = self._load_yaml(hsmusic_album_folder, album_path)
        # Process links first
        link_list = [
            link
            for album_datum in album_data
            for link in album_datum.get('URLs', [])
        ]
        self._import_links(link_list)

        tracks_to_create = []
        locations_to_create = []
        characters_to_create = []
        tags_to_create = []
        track_urls_to_create = []
        commentaries_to_create = []
        album_commentaries_to_create = []
        album_urls_to_create = []
        album_groups_to_create = []
        album_files_to_create = []
        track_commentary_to_create = []
        track_artists_to_create = []
        track_albums_to_create = []

        processed_album = None  # another positional yaml...
        album_artists = []
        track_number = 1
        for album_datum in album_data:
            album = album_datum.get('Album')
            track = album_datum.get('Track')
            if album is not None:
                print(f'Processing album: {album}')
                short_id = album_datum.get('Directory', self._normalize_utf(album))
                processed_album = Album(
                    short_id=short_id, name=album,
                    release_date=self._yaml_date_to_date(album_datum.get('Date')),
                    color=self._yaml_color_to_color(album_datum.get('Color')),
                    cover_art=self._arts_dict.get(short_id)
                )
                album_artists = album_datum.get('Artists', [])
                if album_datum.get('Art Tags') is not None and len(album_datum.get('Art Tags')) > 0:
                    album_art = self._arts_dict.get(short_id)
                    # output all parts of the art tag
                    tags = [tag for tag in album_datum.get('Art Tags') if ':' not in tag]  # Ignore CWs
                    art_locations = [self._locations_dict[tag] for tag in tags]
                    art_characters = [self._characters_dict[tag] for tag in tags]
                    album_art.locations.set(art_locations)
                    album_art.characters.set(art_characters)
                # Only safe because we checked links first
                album_links = [self._links_dict.get(url) for url in album_datum.get('URLs', [])]
                album_groups = [self._groups_dict.get(group) for group in album_datum.get('Groups', [])]
                album_files = self._album_files_dict.get(short_id, [])
                album_commentary = album_datum.get('Commentary')
                if album_commentary is not None:
                    commentary = Commentary(short_id=short_id, text=album_commentary)
                    commentaries_to_create.append(commentary)
                    album_commentaries_to_create.append(
                        Album.commentary.through(album=processed_album, commentary=commentary)
                    )
                album_urls_to_create.extend([
                    Album.urls.through(album=processed_album, link=url)
                    for url in album_links
                ])
                album_groups_to_create.extend([
                    Album.groups.through(album=processed_album, group=group)
                    for group in album_groups
                ])
                album_files_to_create.extend([
                    Album.files.through(album=processed_album, file=file)
                    for file in album_files
                ])

                self._albums_dict[short_id] = processed_album
                self._albums_dict[album] = processed_album
                self._albums_dict[f"album:{short_id}"] = processed_album
            elif track is not None:
                short_id = album_datum.get('Directory', self._normalize_utf(track))
                tags = set(album_datum.get('Art Tags', []))
                if short_id in self._tracks_dict:
                    print(f'Track {track} already exists, updating and adding to album')
                    processed_track = self._tracks_dict[short_id]
                    if processed_album.release_date < processed_track.release_date:
                        # Means we found the original version of a track
                        processed_track.name = track
                        processed_track.release_date = processed_album.release_date
                else:
                    print(f'Adding track: {track}')
                    track_duration = self._yaml_duration_to_timedelta(album_datum.get('Duration'))
                    processed_track = Track(short_id=short_id, name=track,
                                            duration=track_duration,
                                            lyrics=album_datum.get('Lyrics'),
                                            release_date=processed_album.release_date)
                    tracks_to_create.append(processed_track)
                    self._tracks_dict[short_id] = processed_track
                    self._tracks_dict[track] = processed_track
                    self._tracks_dict[f"track:{short_id}"] = processed_track

                    # Create intermediate tables
                    if len(tags) > 0:
                        track_locations = [self._locations_dict.get(location) for location in tags if
                                           location in self._locations_dict]
                        track_characters = [self._characters_dict.get(character) for character in tags if
                                            character in self._characters_dict]
                        track_tags = [self._tags_dict.get(tag) for tag in tags if tag in self._tags_dict]

                        for location, character, tag in zip(track_locations, track_characters, track_tags):
                            locations_to_create.append(
                                Track.locations.through(track=processed_track, location=location))
                            characters_to_create.append(
                                Track.characters.through(track=processed_track, character=character))
                            tags_to_create.append(Track.tags.through(track=processed_track, tag=tag))
                    artist_tuples = self._get_artist_tuples(album_datum.get('Artists', []))
                    if len(artist_tuples) == 0:
                        # Use album creators as artists
                        for artist_name in album_artists:
                            artist_tuples.append((self._artists_dict[artist_name], ArtistType.MUSICIAN, None))
                    track_artists_to_create.extend([
                        TrackArtist(track=processed_track, artist=artist, artist_type=artist_type, notes=artist_roles)
                        for (artist, artist_type, artist_roles) in artist_tuples
                    ])

                for url in [self._links_dict.get(url) for url in album_datum.get('URLs', [])]:
                    track_urls_to_create.append(Track.urls.through(track=processed_track, link=url))

                # Technically commentary should be assigned on a TrackAlbum based when you think about it, but
                # since it's the exact same track it's doubtful it'll ever be relevant
                track_commentary = album_datum.get('Commentary')
                # We will convert it to individual artist commentary later, I guess
                if track_commentary is not None:
                    commentary = Commentary(
                        short_id=f"{processed_album.short_id}-{short_id}",
                        text=track_commentary)
                    commentaries_to_create.append(commentary)
                    track_commentary_to_create.append(
                        Track.commentary.through(track=processed_track, commentary=commentary)
                    )

                # This would be the point to add track references, but we can't yet...
                # Some tracks reference tracks that are processed later
                # So we'll pick up all base tracks and then run through the soundtrack a second time
                # to link them together
                # have I mentioned how great the current yamls are? god I love inventing a format and a parser
                # to create a new set of solutions and problems that need to be solved
                track_album = TrackAlbum(
                    track=processed_track,
                    alias=track,
                    album=processed_album,
                    position=track_number,
                    track_art=self._arts_dict.get(f"{processed_album.short_id}-{processed_track.short_id}")
                )
                track_albums_to_create.append(track_album)
                track_number += 1
        print(f'Processed album {album_path}')
        if processed_album:
            creation_dict = {
                'album': processed_album,
                'tracks': tracks_to_create,
                'locations': locations_to_create,
                'characters': characters_to_create,
                'tags': tags_to_create,
                'track_urls': track_urls_to_create,
                'commentaries': commentaries_to_create,
                'album_commentaries': album_commentaries_to_create,
                'album_urls': album_urls_to_create,
                'album_groups': album_groups_to_create,
                'album_files': album_files_to_create,
                'track_commentaries': track_commentary_to_create,
                'track_artists': track_artists_to_create,
                'track_albums': track_albums_to_create,
            }
            return creation_dict

    def _import_groups(self):
        groups = self._load_yaml(self._wiki_data_folder, 'groups.yaml')
        groups_to_create = []
        # Process links first
        link_list = [
            link
            for group in groups
            for link in group.get('URLs', [])
        ]
        self._import_links(link_list)
        # For recently created artists, artist short id to array of links
        group_link_dict = {}
        print('Processing groups...')
        print(f'Found {len(groups)} groups')
        color = '000000'
        group_type = GroupType.OFFICIAL
        for group in groups:
            # Sadly, the original yaml has order-encoded information for some unholy reason
            # To process the colors, we have no other choice
            if group.get('Group') is None:
                color = self._yaml_color_to_color(group.get('Color'))
                category = group.get('Category')
                if category in ['Fan-musician groups', 'Solo musicians', 'Fandom projects']:
                    group_type = GroupType.FANS
                elif category == 'Projects beyond Homestuck':
                    group_type = GroupType.NONMSPA
                else:
                    group_type = GroupType.OFFICIAL
            else:
                short_id = group.get('Directory', self._normalize_utf(group.get('Group')))
                print(f'Processing {short_id}...')
                processed_group = Group(short_id=short_id,
                                        name=group.get('Group'), description=group.get('Description'),
                                        color=color, type=group_type)
                # Only safe because we checked links first
                links = [self._links_dict.get(url) for url in group.get('URLs', [])]
                group_link_dict[short_id] = links
                groups_to_create.append(processed_group)
        created_groups = Group.objects.bulk_create(groups_to_create)
        for group in created_groups:
            group.urls.set(group_link_dict.get(group.short_id, []))
            self._groups_dict[f"group:{group.short_id}"] = group
            self._groups_dict[group.short_id] = group
            self._groups_dict[group.name] = group
        print('Imported all groups!')

    def _import_album_references(self, hsmusic_album_folder, album_path):
        existing_album = None
        track_references_to_create = []
        for album_datum in self._load_yaml(hsmusic_album_folder, album_path):
            album = album_datum.get('Album')
            track = album_datum.get('Track')
            if album is not None:
                short_id = album_datum.get('Directory', self._normalize_utf(album))
                existing_album = self._albums_dict.get(short_id)
            if track is not None:
                print(f'Processing track for references: {track}')
                short_id = album_datum.get('Directory', self._normalize_utf(track))
                existing_track = self._tracks_dict.get(short_id)
                track_references = [
                    TrackReference(referencing_track=existing_track, referenced_track=self._tracks_dict.get(reference))
                    for reference in album_datum.get('Referenced Tracks', [])
                ]
                print(f'Found {len(track_references)} references')
                track_references_to_create.extend(track_references)
        if existing_album is None:
            return None
        return {
            'album': existing_album,
            'track_references': track_references_to_create,
        }

    def _import_artists(self):
        artists = self._load_yaml(self._wiki_data_folder, 'artists.yaml')
        artists_to_create = []
        # Process links first
        link_list = [
            link
            for artist in artists
            for link in artist.get('URLs', [])
        ]
        self._import_links(link_list)

        # For recently created artists, artist short id to array of links
        artist_urls_to_create = []
        print('Processing artists...')
        print(f'Found {len(artists)} artists')
        for artist in artists:
            short_id = artist.get('Directory', self._normalize_utf(artist.get('Artist')))
            print(f'Processing {short_id}...')
            processed_artist = Artist(short_id=short_id, name=artist.get('Artist'),
                                      aliases=artist.get('Aliases'), artist_types=[ArtistType.MUSICIAN])
            # Only safe because we checked links first
            for link in [self._links_dict.get(url) for url in artist.get('URLs', [])]:
                artist_urls_to_create.append(Artist.urls.through(artist=processed_artist, link=link))
            artists_to_create.append(processed_artist)
        created_artists = Artist.objects.bulk_create(artists_to_create)
        Artist.urls.through.objects.bulk_create(artist_urls_to_create)
        print('Imported all artists!')

        for artist in created_artists:
            self._artists_dict[f"artist:{artist.short_id}"] = artist
            self._artists_dict[artist.name] = artist
            self._artists_dict[artist.short_id] = artist

    def _import_characters_locations_and_tags(self):
        # Note yes, this is stupid because we're using the same file to create three different
        # entities, but it's because we'll just remove the extra ones later by hand, easier than "moving"
        # which would be deleting and creating anyway
        locations_to_create = []
        characters_to_create = []
        tags_to_create = []
        tags = self._load_yaml(self._wiki_data_folder, 'tags.yaml')
        for tag in tags:
            tag_name = tag.get('Tag')
            short_id = tag.get('Directory', self._normalize_utf(tag_name))
            location = Location(short_id=short_id, name=tag_name,
                                color=self._yaml_color_to_color(tag.get('Color')))
            character = Character(short_id=short_id, name=tag_name,
                                  color=self._yaml_color_to_color(tag.get('Color')))
            tag = Tag(short_id=short_id, name=tag_name,
                      color=self._yaml_color_to_color(tag.get('Color')))
            locations_to_create.append(location)
            characters_to_create.append(character)
            tags_to_create.append(tag)
        locations = Location.objects.bulk_create(locations_to_create)
        characters = Character.objects.bulk_create(characters_to_create)
        tags = Tag.objects.bulk_create(tags_to_create)
        self._characters_dict = {character.name: character for character in characters}
        self._locations_dict = {location.name: location for location in locations}
        self._tags_dict = {tag.name: tag for tag in tags}

    def _import_links(self, url_list: list[str]):
        links_to_create = []
        print(f'Processing {len(url_list)} links...')
        for url in url_list:
            processed_link = self._links_dict.get(url, Link(link=url))
            if not processed_link.pk:
                if self._check_links:
                    processed_link.is_dead = self._is_link_alive(url)
                processed_link.link_type = Link.get_link_type(url)
                links_to_create.append(processed_link)

        created_links = Link.objects.bulk_create(links_to_create)

        for link in created_links:
            self._links_dict[link.link] = link

    # Gets manageable artist/role tuples from Contributors/Artists yaml fields
    def _get_artist_tuples(self, yaml_artists: list[str], default_role=ArtistType.MUSICIAN):
        if len(yaml_artists) == 0 or yaml_artists is None:
            return []
        artist_tuples = []
        if yaml_artists[0] == '<i>See [[flash:5263]].</i>':
            # I hate that this is even needed, this is not how data entities work
            yaml_artists = [
                'Amanda H. (art)',
                'Chaz Canterbury (art)',
                'Lexxy (art)',
                'Paige Turner (art)',
                'Scarodactyl (art)',
                'Hanni Brosh (art)',
                'Lauren Ross (art)',
                'Vivian Ng (art)',
                'Xamag (art)',
                'Tanney Liu (art)'
            ]
        for musician in yaml_artists:
            # Artists come with NAME and ROLES, like this, "Artist (roles)"
            # We will split them up and create the artist if necessary
            # If there is a parenthesis, we split on it, otherwise we just use the whole string
            if '(' in musician:
                artist_name = musician.split('(')[0].strip()
                artist_roles = musician.split('(')[1].split(')')[0].split(',')
                artist_type = ArtistType.get_artist_type_from_string(artist_roles[0])
                artist_tuples.append((self._artists_dict[artist_name], artist_type, ' '.join(artist_roles)))
            else:
                artist_tuples.append((self._artists_dict[musician], default_role, None))
        return artist_tuples

    @staticmethod
    def _yaml_color_to_color(string):
        # Just adds a default black value if the color is not specified
        return string if string is not None else '#000000'

    @staticmethod
    def _yaml_duration_to_timedelta(string: str | int) -> timedelta | None:
        # Converts strings like 4:33 and 1:04:33 to hours, minutes, seconds
        if string is None:
            return None
        if not isinstance(string, str):
            # For some reason, some durations in yaml are ints, which convert to seconds
            input_seconds: int = string
            hours = input_seconds // 3600
            minutes = input_seconds // 60 - hours * 60
            seconds = input_seconds - (hours * 3600) - (minutes * 60)
            print(f'Converted {string} to {hours}:{minutes}:{seconds}')
        else:
            split = string.split(':')
            if len(split) == 2:
                hours = 0
                minutes = int(split[0])
                seconds = int(split[1])
            elif len(split) == 3:
                hours = int(split[0])
                minutes = int(split[1])
                seconds = int(split[2])
            else:
                raise ValueError(f'Invalid duration: {string}')
        return timedelta(hours=hours, minutes=minutes, seconds=seconds)

    @staticmethod
    def _yaml_date_to_date(date_string):
        # Converts a string with the format April 21, 2012 or Month DD, YYYY to a python date
        if date_string is None:
            return None
        # Remove hour strings, yaml has them as a hack
        hour_strings = ['12:00:00', '12:00:01', '00:00:04', '00:00:05']
        for hour_string in hour_strings:
            date_string = date_string.replace(f" {hour_string}", '')
        # Dates can still be malformed and missing commas, so we have an alternate way
        # of parsing them
        try:
            return datetime.strptime(date_string, '%B %d, %Y').date()
        except ValueError:
            return datetime.strptime(date_string, '%B %d %Y').date()

    @staticmethod
    def _normalize_utf(string):
        print(f'Normalizing {string}')
        # Uses Nebula logic for consistency
        track_name = re.split(' ', string)
        track_name = "-".join(track_name)
        track_name = re.sub('&', 'and', track_name)
        track_name = re.sub('[^a-zA-Z0-9\-]', '', track_name)
        track_name = re.sub('-{2,}', '-', track_name)
        track_name = re.sub('^-+|-+$', '', track_name).lower()
        return track_name

    @staticmethod
    def _is_link_alive(url_string):
        alivelist = ['mspfa']
        for alive in alivelist:
            if alive in url_string:
                return True
        # Wait 0.5 second to avoid rate limits
        time.sleep(0.5)
        try:
            request = urllib.request.urlopen(url_string)
            request_code = request.getcode()
            if not request_code == 200:
                print(f'Link {url_string} has a different valid code: {request_code}')
            return True
        except urllib.error.HTTPError as e:
            print(f'Link {url_string} might be dead through HTTP error: {e}')
            return False
        except urllib.error.URLError as e:
            print(f'Link {url_string} is dead through URL error: {e}')
            return False
        except Exception as e:
            print(f'Link {url_string} is dead: {e}')
            return False

    @staticmethod
    def _load_yaml(hsmusic_folder, filename):
        file_path = os.path.join(hsmusic_folder, filename)
        file = open(file_path, 'r', encoding='utf-8')
        contents = list(yaml.load_all(file.read(), Loader=yaml.FullLoader))
        file.close()
        return contents
