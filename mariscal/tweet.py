import tweepy

from pyramid.threadlocal import get_current_registry


class TweetUtil:
    _session = dict()

    def __init__(self, user):
        settings = get_current_registry().settings
        self._auth = tweepy.OAuthHandler(settings.get('consumer_key'), settings.get('consumer_secret'))
        if user.is_twitter_account_exist():
            self._auth.set_access_token(user.twitter_access_token, user.twitter_access_token_secret)
            self._api = tweepy.API(self._auth)

    def get_authenticate_url(self):
        authenticate_url = self._auth.get_authorization_url()
        TweetUtil._session['request_token'] = self._auth.request_token

        return authenticate_url

    def auth_twitter_access_token(self, pin_code, user):
        self._auth.request_token = TweetUtil._session.get('request_token')
        access_token = self._auth.get_access_token(verifier=pin_code)

        if access_token:
            self._auth.set_access_token(access_token[0], access_token[1])
            user.set_twitter_access_token(access_token)

        # TODO: error handling
        else:
            pass

    def get_tweets(self):
        return self._api.user_timeline()

