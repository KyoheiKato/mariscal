from .models import (
    User,
    Mock,
    Comment,
    )

from pyramid.view import (
    view_config,
    forbidden_view_config,
    )

from pyramid.security import (
    remember,
    forget,
    authenticated_userid,
    )

from pyramid.httpexceptions import (
    HTTPFound,
    )

from pyramid.response import Response

from .tweet import *


class HomeView(object):
    def __init__(self, request):
        self.request = request

    @forbidden_view_config()
    def forbidden_view(self):
        return HTTPFound(location=self.request.route_url('login'))

    @view_config(route_name='home', request_method='GET', renderer='templates/home.jinja2', permission='view')
    def home_view(self):
        user = User.find_by_id(authenticated_userid(self.request))
        mocks = Mock.find_all()

        return dict(user=user, mocks=mocks)

    @view_config(route_name='login', request_method='GET', renderer='templates/login.jinja2')
    def login_get(self):
        return dict()

    @view_config(route_name='login', request_method='POST', renderer='templates/login.jinja2')
    def login_post(self):
        name = self.request.params.get('username')
        password = self.request.params.get('password')
        user = User.find_by_name(name)
        if user and user.verify_password(password):
            headers = remember(self.request, user.id)

            return HTTPFound(location=self.request.route_url('home'), headers=headers)

        message = 'Login Failed'

        return dict(message=message)

    @view_config(route_name='logout', request_method='GET', renderer='templates/logout.jinja2')
    def logout_view(self):
        headers = forget(self.request)
        return HTTPFound(location=self.request.route_url('home'), headers=headers)

    @view_config(route_name='sign_up', request_method='GET', renderer='templates/sign_up.jinja2')
    def sign_up_get(self):
        return dict()

    @view_config(route_name='sign_up', request_method='POST', renderer='templates/sign_up.jinja2')
    def sign_up_post(self):
        name = self.request.params.get('username')
        password = self.request.params.get('password')
        if User.find_by_name(name) is None:
            User.add_user(User(name, password))

            return HTTPFound(location=self.request.route_url('login'))

        message = 'Sign up failed'

        return dict(message=message)


class MockView(object):
    def __init__(self, request):
        self.request = request
        self.user = User.find_by_id(authenticated_userid(self.request))

    @view_config(route_name='mocks', request_method='GET', renderer='templates/mock/mocks.jinja2', permission='view')
    def mock_list_view(self):
        mocks = Mock.find_all()

        return dict(mocks=mocks, user=self.user)

    @view_config(route_name='view_mock', renderer='templates/mock/view_mock.jinja2', permission='view')
    def view_mock_post(self):
        mock = Mock.find_by_id(self.request.matchdict.get('mock_id'))

        if 'form.submitted' in self.request.params:
            return HTTPFound(location=self.request.route_url('edit_mock', mock_id=mock.id))

        if 'comment.submitted' in self.request.params:
            content = self.request.params.get('comment')
            Comment.add_comment(Comment(content, self.user.id, mock.id))

            return HTTPFound(location=self.request.route_url('view_mock', mock_id=mock.id))

        return dict(user=self.user, mock=mock, author=mock.user)

    @view_config(route_name='new_mock', request_method='GET', renderer='templates/mock/new_mock.jinja2', permission='view')
    def new_mock_get(self):
        return dict(user=self.user)

    @view_config(route_name='new_mock', request_method='POST', renderer='templates/mock/new_mock.jinja2', permission='view')
    def new_mock_post(self):
        title = self.request.params.get('title')
        content = self.request.params.get('content')
        Mock.add_mock(Mock(title, content, self.user.id))

        return HTTPFound(location=self.request.route_url('home'))

    @view_config(route_name='edit_mock', renderer='templates/mock/edit_mock.jinja2', permission='view')
    def edit_mock(self):
        mock = Mock.find_by_id(self.request.matchdict['mock_id'])

        if 'form.submitted' in self.request.params:
            mock.title = self.request.params.get('title')
            mock.content = self.request.params.get('comment')
            Mock.add_mock(mock)

            return HTTPFound(location=self.request.route_url('view_mock', mock_id=mock.id))

        return dict(mock=mock, user=self.user)


class TweetView(object):
    def __init__(self, request):
        self.request = request
        self.user = User.find_by_id(authenticated_userid(self.request))
        self.tweet_util = TweetUtil()

    @view_config(route_name='tweets', request_method='GET', permission='view', renderer='templates/timeline.jinja2')
    def view_mock_list(self):
        tweets = self.tweet_util.get_tweets()

        return dict(user=self.user, tweets=tweets)


class AjaxAPI(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='ajax_api', request_method='POST', permission='view', xhr=True, renderer="json")
    def ajax_post(self):
        ajax_id = self.request.matchdict.get('ajax_id')

        if ajax_id == 'evaluate':
            mock = Mock.find_by_id(self.request.params.get('mock'))
            user = User.find_by_id(self.request.params.get('user'))
            state = self.request.params.get('state')
            value = self.request.params.get('value')

            print(mock.id)

            if value == 'good.submitted':
                if state == 'active':
                    user.delete_good_mock(mock)
                else:
                    user.add_good_mock(mock)
                state = user in mock.good_users
            elif value == 'bad.submitted':
                if state == 'active':
                    user.delete_bad_mock(mock)
                else:
                    user.add_bad_mock(mock)
                state = user in mock.bad_users

            if value == 'good.submitted':
                return dict(number=len(mock.good_users), state=state)
            elif value == 'bad.submitted':
                return dict(number=len(mock.bad_users), state=state)
            else:
                return dict()

        if ajax_id == 'tweet':
            tweet_util = TweetUtil()
            tweet_util.post_tweet(self.request.params.get('text'))

            return Response('OK')
