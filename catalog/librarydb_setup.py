import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=True)
    email = Column(String(250), nullable=True)
    picture = Column(String(250))


class Genre(Base):
    __tablename__ = 'genre'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=True)


class Library(Base):
    __tablename__ = 'library'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
          'name': self.name,
          'id': self.id,
          'user': self.user.name
        }


class Book(Base):
    __tablename__ = 'book'

    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    author = Column(String(80))
    description = Column(String(250))
    genre_id = Column(Integer, ForeignKey('genre.id'))
    genre = relationship(Genre)
    library_id = Column(Integer, ForeignKey('library.id'))
    library = relationship(Library)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
          'title': self.title,
          'id': self.id,
          'author': self.author,
          'genre': self.genre.name,
          'description': self.description,
        }


engine = create_engine('sqlite:///library.db')

Base.metadata.create_all(engine)
