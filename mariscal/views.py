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


@view_config(route_name='home', request_method='GET', renderer='templates/home.jinja2', permission='view')
def home_view(request):
    user = User.find_by_id(authenticated_userid(request))
    mocks = Mock.find_all()

    return dict(user=user, mocks=mocks)


@view_config(route_name='home', request_method='POST', permission='view', xhr=True, renderer="json")
def evaluate_mock(request):
    mock = Mock.find_by_id(request.POST['mock'])
    user = User.find_by_id(request.POST['user'])
    state = request.POST['state']
    value = request.POST['value']

    if value == 'good.submitted':
        if state == 'active':
            user.delete_good_mock(mock)
        elif state == 'deactive':
            user.add_good_mock(mock)
        state = user in mock.good_users
    elif value == 'bad.submitted':
        if state == 'active':
            user.delete_bad_mock(mock)
        elif state == 'deactive':
            user.add_bad_mock(mock)
        state = user in mock.bad_users

    if value == 'good.submitted':
        return dict(number=len(mock.good_users), state=state)
    elif value == 'bad.submitted':
        return dict(number=len(mock.bad_users), state=state)
    else:
        return dict()


@forbidden_view_config(renderer='templates/login.jinja2')
def forbidden_view(request):
    return HTTPFound(location=request.route_url('login'))


@view_config(route_name='login', renderer='templates/login.jinja2')
def login_view(request):
    name = ''
    message = ''
    if 'form.submitted' in request.params:
        name = request.params['username']
        password = request.params['password']
        user = User.find_by_name(name)
        if user is not None and user.verify_password(password):
            headers = remember(request, user.id)
            return HTTPFound(location=request.route_url('home'), headers=headers)

        message = 'Login Failed'

    return dict(name=name, message=message, url=request.application_url + '/login')


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
    author = mock.user
    user = User.find_by_id(authenticated_userid(request))

    if 'form.submitted' in request.params:
        return HTTPFound(location=request.route_url('edit_mock', mock_id=mock.id))

    if 'comment.submitted' in request.params:
        content = request.params['comment']
        Comment.add_comment(Comment(content, user.id, mock.id))

        return HTTPFound(location=request.route_url('view_mock', mock_id=mock.id))

    return dict(mock=mock, author=author, user=user)


@view_config(route_name='new_mock', renderer='templates/mock/new_mock.jinja2', permission='view')
def new_mock(request):
    user = User.find_by_id(authenticated_userid(request))

    if 'form.submitted' in request.params:
        title = request.params['title']
        content = request.params['content']
        Mock.add_mock(Mock(title, content, user.id))

        return HTTPFound(location=request.route_url('home'))

    return dict(user=user)


@view_config(route_name='edit_mock', renderer='templates/mock/edit_mock.jinja2', permission='view')
def edit_mock(request):
    mock = Mock.find_by_id(request.matchdict['mock_id'])
    user = User.find_by_id(authenticated_userid(request))

    if 'form.submitted' in request.params:
        mock.title = request.params['title']
        mock.content = request.params['content']
        Mock.add_mock(mock)

        return HTTPFound(location=request.route_url('view_mock', mock_id=mock.id))

    return dict(mock=mock, user=user)