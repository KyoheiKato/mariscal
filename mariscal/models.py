import hashlib
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    DateTime,
    Table,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    relation,
    )

from zope.sqlalchemy import ZopeTransactionExtension

from pyramid.security import (
    Allow,
    )

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

user_good_mock_table = Table(
    'user_good_mocks',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('mock_id', Integer, ForeignKey('mocks.id')),
    )

user_bad_mock_table = Table(
    'user_bad_mocks',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('mock_id', Integer, ForeignKey('mocks.id')),
    )


class User(Base):
    __tablename__ = 'users'
    query = DBSession.query_property()
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    _password = Column(Text, nullable=False)
    create_mocks = relationship("Mock", backref="user")
    comments = relationship("Comment", backref="user")
    twitter_access_token = Column(Text)
    twitter_access_token_secret = Column(Text)
    good_mocks = relation('Mock',
                          order_by='Mock.id',
                          uselist=True,
                          backref='good_users',
                          secondary=user_good_mock_table)
    bad_mocks = relation('Mock',
                         order_by='Mock.id',
                         uselist=True,
                         backref='bad_users',
                         secondary=user_bad_mock_table)
    group = ['USERS']

    def __init__(self, name, password):
        self.name = name
        self.password = password

    def __eq__(self, other):
        return self.id == other.id

    def _set_password(self, password):
        self._password = hashlib.sha1(password.encode('utf-8')).hexdigest()

    def verify_password(self, password):
        return self._password == hashlib.sha1(password.encode('utf-8')).hexdigest()

    def add_good_mock(self, mock):
        self.good_mocks.append(mock)
        DBSession.add(self)

    def add_bad_mock(self, mock):
        self.bad_mocks.append(mock)
        DBSession.add(self)

    def delete_good_mock(self, mock):
        self.good_mocks.remove(mock)
        DBSession.add(self)

    def delete_bad_mock(self, mock):
        self.bad_mocks.remove(mock)
        DBSession.add(self)

    def is_twitter_account_exist(self):
        return self.twitter_access_token and self.twitter_access_token_secret

    def set_twitter_access_token(self, token):
        self.twitter_access_token = token[0]
        self.twitter_access_token_secret = token[1]

    @classmethod
    def find_by_id(cls, user_id):
        return cls.query.filter(cls.id == user_id).first()

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter(cls.name == name).first()

    @classmethod
    def add_user(cls, user):
        DBSession.add(user)

    password = property(fset=_set_password)


class Mock(Base):
    __tablename__ = 'mocks'
    query = DBSession.query_property()
    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    time = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    comments = relationship("Comment", backref="mock")

    def __init__(self, title, content, user_id):
        self.title = title
        self.content = content
        self.user_id = user_id
        self.time = datetime.now()

    def __eq__(self, other):
        return self.id == other.id

    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter(cls.id == id).first()

    @classmethod
    def add_mock(cls, mock):
        DBSession.add(mock)


class Comment(Base):
    __tablename__ = 'comments'
    query = DBSession.query_property()
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    time = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    mock_id = Column(Integer, ForeignKey('mocks.id'), nullable=False)

    def __init__(self, content, user_id, mock_id):
        self.content = content
        self.time = datetime.now()
        self.user_id = user_id
        self.mock_id = mock_id

    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def add_comment(cls, comment):
        DBSession.add(comment)


class TwitterAccount(Base):
    __tablename__ = 'twitter_accounts'
    query = DBSession.query_property()
    id = Column(Integer, primary_key=True)
    account_id = Column(Text, nullable=False)
    _account_password = Column(Text, nullable=False)

    def __init__(self, account_id, account_password):
        self.account_id = account_id
        self.account_password = account_password

    def _set_account_password(self, account_password):
        self._account_password = hashlib.sha1(account_password.encode('utf-8')).hexdigest()

    account_password = property(fset=_set_account_password)


class RootFactory(object):
    __acl__ = [(Allow, 'USERS', 'view')]

    def __init__(self, request):
        pass
