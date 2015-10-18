import tweepy

from pyramid.threadlocal import get_current_registry


class TweetUtil:
    def __init__(self):
        settings = get_current_registry().settings
        self._auth = tweepy.OAuthHandler(settings.get('consumer_key'), settings.get('consumer_secret'))

    def get_authenticate_url(self):
        return self._auth.get_authorization_url()
