from django.db import models


class LinkType(models.TextChoices):
    YOUTUBE = 'youtube', 'Youtube'
    TWITTER = 'twitter', 'Twitter'
    INSTAGRAM = 'instagram', 'Instagram'
    TUMBLR = 'tumblr', 'Tumblr'
    WEBSITE = 'website', 'Website'
    BANDCAMP = 'bandcamp', 'Bandcamp'
    SOUNDCLOUD = 'soundcloud', 'Soundcloud'
    BGRECO = 'bgreco', 'Bgreco.net archive'
    SPOTIFY = 'spotify', 'Spotify'
    OTHER = 'other', 'Other'


class Link(models.Model):
    link = models.CharField(max_length=512, blank=False, null=False)
    is_dead = models.BooleanField(default=False)
    link_type = models.CharField(max_length=32, choices=LinkType.choices, default=LinkType.WEBSITE)

    def __str__(self):
        return self.link

    @staticmethod
    def get_link_type(link_string):
        if 'youtu' in link_string:
            return LinkType.YOUTUBE
        elif 'twitter' in link_string:
            return LinkType.TWITTER
        elif 'instagram' in link_string:
            return LinkType.INSTAGRAM
        elif 'bandcamp' in link_string:
            return LinkType.BANDCAMP
        elif 'bgreco' in link_string:
            return LinkType.BGRECO
        elif 'soundcloud' in link_string:
            return LinkType.SOUNDCLOUD
        elif 'spotify' in link_string:
            return LinkType.SPOTIFY
        elif 'tumblr' in link_string:
            return LinkType.TUMBLR
        return LinkType.WEBSITE
