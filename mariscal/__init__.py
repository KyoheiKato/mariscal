import configparser

from pyramid.config import Configurator

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy


from sqlalchemy import engine_from_config

from .security import groupfinder

from .models import (
    DBSession,
    Base,
    RootFactory
    )


def _load_secret_keys(settings):
    secret_ini = settings.get('twitter.key.path', None)
    config = configparser.ConfigParser()
    config.read(secret_ini)

    for k, v in config.items('twitter:keys'):
        settings.update({k:v})

    return settings


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    _load_secret_keys(settings)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    authn_policy = AuthTktAuthenticationPolicy('sosecret', callback=groupfinder, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(settings=settings, root_factory='mariscal.models.RootFactory')

    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    config.include('pyramid_chameleon')
    config.include('pyramid_jinja2')

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('sign_up', '/sign_up')
    config.add_route('tweets', '/tweets')
    config.add_route('mocks', '/mocks')
    config.add_route('new_mock', '/mock/new_mock')
    config.add_route('view_mock', '/mock/{mock_id}')
    config.add_route('edit_mock', '/mock/{mock_id}/edit')
    config.add_route('tweet_post_api', '/ajax/tweet_post')
    config.add_route('good_api', '/ajax/good_post')
    config.add_route('bad_api', '/ajax/bad_post')

    config.scan()

    return config.make_wsgi_app()
