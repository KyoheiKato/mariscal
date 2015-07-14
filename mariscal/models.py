import hashlib
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    DateTime,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    )

from zope.sqlalchemy import ZopeTransactionExtension

from pyramid.security import (
    Allow,
    )

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    query = DBSession.query_property()
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    _password = Column(Text, nullable=False)
    mocks = relationship("Mock", backref="user")
    group = ['USERS']

    def __init__(self, name, password):
        self.name = name
        self.password = password

    def _set_password(self, password):
        self._password = hashlib.sha1(password.encode('utf-8')).hexdigest()

    def verify_password(self, password):
        return self._password == hashlib.sha1(password.encode('utf-8')).hexdigest()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter(cls.id == id).first()

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
    mock_id = Column(Integer, ForeignKey('mocks.id'), nullable=False)

    def __init__(self, content):
        self.content = content


class RootFactory(object):
    __acl__ = [(Allow, 'USERS', 'view')]

    def __init__(self, request):
        pass