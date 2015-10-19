import tweepy

from pyramid.threadlocal import get_current_registry


class TweetUtil:
    __session = dict()

    def __init__(self, user):
        settings = get_current_registry().settings
        self.__auth = tweepy.OAuthHandler(settings.get('consumer_key'), settings.get('consumer_secret'))
        if user.is_twitter_account_exist():
            self.__auth.set_access_token(user.twitter_access_token, user.twitter_access_token_secret)
            self.__api = tweepy.API(self.__auth)

    def get_authenticate_url(self):
        authenticate_url = self.__auth.get_authorization_url()
        TweetUtil.__session['request_token'] = self.__auth.request_token

        return authenticate_url

    def auth_twitter_access_token(self, pin_code, user):
        self.__auth.request_token = TweetUtil.__session.get('request_token')
        access_token = self.__auth.get_access_token(verifier=pin_code)

        if access_token:
            self.__auth.set_access_token(access_token[0], access_token[1])
            user.set_twitter_access_token(access_token)

        # TODO: error handling
        else:
            pass

    def get_tweets(self):
        return self.__api.user_timeline()

