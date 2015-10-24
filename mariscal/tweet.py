import tweepy

from pyramid.threadlocal import get_current_registry


class TweetUtil:
    __instance = None
    __session = dict()

    def __init__(self, user):
        settings = get_current_registry().settings
        self.__auth = tweepy.OAuthHandler(settings.get('consumer_key'), settings.get('consumer_secret'))
        if user.is_twitter_account_exist():
            print('init')
            self.__auth.set_access_token(user.twitter_access_token, user.twitter_access_token_secret)
            self.__api = tweepy.API(self.__auth)

    def __new__(cls, *args, **kwargs):
        if TweetUtil.__instance is None:
            TweetUtil.__instance = object.__new__(cls)

        return TweetUtil.__instance

    def get_authenticate_url(self):
        authenticate_url = self.__auth.get_authorization_url().replace('authorize', 'authenticate')
        TweetUtil.__session['request_token'] = self.__auth.request_token

        return authenticate_url

    def auth_twitter_access_token(self, oauth_verifier, user):
        self.__auth.request_token = TweetUtil.__session.get('request_token')

        # TODO: error handling
        self.__auth.get_access_token(oauth_verifier)
        user.set_twitter_access_token(self.__auth.access_token, self.__auth.access_token_secret)
        self.__api = tweepy.API(self.__auth)

    def get_tweets(self):
        print(self.__api.user_timeline())
        return self.__api.user_timeline()
