import tweepy

from pyramid.threadlocal import get_current_registry


class TweetUtil:
    __session = dict()

    def __init__(self, user, request):
        settings = get_current_registry().settings
        self.__auth = tweepy.OAuthHandler(settings.get('consumer_key'), settings.get('consumer_secret'))
        if user.is_twitter_account_exist():
            self.__auth.set_access_token(user.twitter_access_token, user.twitter_access_token_secret)
            self.__api = tweepy.API(self.__auth)

    def get_authenticate_url(self):
        authenticate_url = self.__auth.get_authorization_url().replace('authorize', 'authenticate')
        TweetUtil.__session['request_token'] = self.__auth.request_token

        return authenticate_url

    def auth_twitter_access_token(self, oauth_token, oauth_verifier, user):
        self.__auth.request_token = TweetUtil.__session.get('request_token')

        # TODO: error handling
        self.__auth.set_access_token(oauth_token, oauth_verifier)
        user.set_twitter_access_token(oauth_token, oauth_verifier)

    def get_tweets(self):
        return self.__api.user_timeline()
