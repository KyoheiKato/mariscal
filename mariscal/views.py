from .models import (
    User,
    Mock,
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


@view_config(route_name='home', renderer='templates/home.jinja2', permission='view')
def home_view(request):
    user = User.find_by_id(authenticated_userid(request))
    mocks = Mock.find_all()

    return dict(user=user, mocks=mocks)


@forbidden_view_config(renderer='templates/login.jinja2')
def forbidden_view(request):
    return HTTPFound(location=request.route_url('login'))


@view_config(route_name='login', renderer='templates/login.jinja2')
def login_view(request):
    name = ''
    password = ''
    message = ''
    if 'form.submitted' in request.params:
        name = request.params['username']
        password = request.params['password']
        user = User.find_by_name(name)
        if user is not None and user.verify_password(password):
            headers = remember(request, user.id)
            return HTTPFound(location=request.route_url('home'), headers=headers)

        message = 'Login Failed'

    return dict(name=name, password=password, message=message, url=request.application_url + '/login')


@view_config(route_name='logout', renderer='templates/logout.jinja2')
def logout_view(request):
    headers = forget(request)
    return HTTPFound(location=request.route_url('home'), headers=headers)


@view_config(route_name='sign_up', renderer='templates/sign_up.jinja2')
def sign_up_view(request):
    message = ''

    if 'form.submitted' in request.params:
        name = request.params['username']
        password = request.params['password']
        if User.find_by_name(name) is None:
            User.add_user(User(name, password))
            return HTTPFound(location=request.route_url('login'))

        message = 'User is already exist'

    return dict(message=message)


@view_config(route_name='view_mock', renderer='templates/mock/view_mock.jinja2', permission='view')
def view_mock(request):
    mock = Mock.find_by_id(request.matchdict['mock_id'])
    user = mock.user

    if 'form.submitted' in request.params:
        return HTTPFound(location=request.route_url('edit_mock', mock_id=mock.id))

    return dict(mock=mock, user=user)


@view_config(route_name='new_mock', renderer='templates/mock/new_mock.jinja2', permission='view')
def new_mock(request):
    user = User.find_by_id(authenticated_userid(request))

    if 'form.submitted' in request.params:
        content = request.params['content']
        Mock.add_mock(Mock(content, user.id))

        return HTTPFound(location=request.route_url('home'))

    return dict(user=user)


@view_config(route_name='edit_mock', renderer='templates/mock/edit_mock.jinja2', permission='view')
def edit_mock(request):
    mock = Mock.find_by_id(request.matchdict['mock_id'])
    user = User.find_by_id(authenticated_userid(request))

    if 'form.submitted' in request.params:
        mock.content = request.params['content']
        Mock.add_mock(mock)

        return HTTPFound(location=request.route_url('view_mock', mock_id=mock.id))

    return dict(mock=mock, user=user)