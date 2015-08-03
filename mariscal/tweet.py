import tweepy

from pyramid.threadlocal import get_current_registry

from celery import task


class TweetUtil:
    def __init__(self):
        settings = get_current_registry().settings

        auth = tweepy.OAuthHandler(settings.get('consumer_key'), settings.get('consumer_secret'))
        auth.set_access_token(settings.get('access_token'), settings.get('access_token_secret'))
        self._api = tweepy.API(auth)

    # @task
    def post_tweet(self, message):
        self._api.update_status(status=message)

    # @task
    def get_tweets(self):
        return self._api.user_timeline()
