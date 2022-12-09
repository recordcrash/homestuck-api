from django.db import models


class ArtistType(models.TextChoices):
    MUSICIAN = 'musician', 'Musician'
    COMPOSER = 'composer', 'Composer'
    LYRICIST = 'lyricist', 'Lyricist'
    VOCALIST = 'vocalist', 'Vocalist'
    INSTRUMENTALIST = 'instrumentalist', 'Instrumentalist'
    ARRANGER = 'arranger', 'Arranger'
    PRODUCER = 'producer', 'Producer'
    ARTIST = 'artist', 'Artist'
    ORGANIZER = 'organizer', 'Organizer'
    IDEA = 'idea', 'Idea'
    WRITER = 'writer', 'Writer'
    DIRECTOR = 'director', 'Director'
    ENGINEER = 'engineer', 'Engineer'
    OTHER = 'other', 'Other'

    @staticmethod
    def get_artist_type_from_string(string):
        # This is spaghetti but we'll fix it by hand later
        for artist_type in ArtistType.choices:
            if artist_type[1].lower() == string.lower():
                return artist_type[0]
        if string.lower() in ['engineering', 'scripting']:
            return ArtistType.ENGINEER
        if string.lower() in ['lyrics', 'lyricists']:
            return ArtistType.LYRICIST
        if string.lower() in ['music', 'musicians']:
            return ArtistType.MUSICIAN
        if string.lower() in ['vocals', 'vocalists', 'sound designer', 'sound design']:
            return ArtistType.VOCALIST
        if string.lower() in ['instrumental', 'instrumentalists']:
            return ArtistType.INSTRUMENTALIST
        if string.lower() in ['arrangement', 'arrangers']:
            return ArtistType.ARRANGER
        if string.lower() in ['producers', 'additional sound', 'production']:
            return ArtistType.PRODUCER
        if string.lower() in ['artist', 'artists', 'environment art', 'cutscene backgrounds',
                              'animation cleanup', 'animation', 'cutscene illustration',
                              'additional art', 'backgrounds', 'endings', 'characters',
                              'sprites']\
                or string.lower().startswith('art:'):
            return ArtistType.ARTIST
        if string.lower() in ['organizer', 'organizers']:
            return ArtistType.ORGANIZER
        if string.lower() in ['idea', 'ideas']:
            return ArtistType.IDEA
        if string.lower() in ['writers', 'lead writer', 'lead writing', 'writing',
                              'additional writing']\
                or string.lower().startswith('writing:'):
            return ArtistType.WRITER
        if string.lower() in ['director', 'directors', 'directing']:
            return ArtistType.DIRECTOR
        return ArtistType.OTHER
