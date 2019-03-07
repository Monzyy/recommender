from sqlalchemy import (BigInteger, Boolean, Column, Date, DateTime, Float,
                        ForeignKey, Integer, String, Table)
from sqlalchemy.orm import relationship

from .database import Base

movie_has_genre_table = Table('movie_has_genre', Base.metadata,
                              Column('movie_id', Integer, ForeignKey('movies.id')),
                              Column('genre_id', Integer, ForeignKey('genres.id')))


class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    summary = Column(String)
    budget = Column(Integer)
    adult = Column(Boolean)
    original_language = Column(String)
    original_title = Column(String)
    poster_path = Column(String)
    release_date = Column(Date)
    revenue = Column(BigInteger)
    runtime = Column(Integer)
    status = Column(String)
    tagline = Column(String)
    video = Column(Boolean)

    ratings = relationship('Rating', back_populates='movie', cascade='all, delete-orphan')
    genres = relationship('Genre', secondary=movie_has_genre_table)


class Rating(Base):
    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    rating = Column(Float)
    created_at = Column(DateTime)
    movie_id = Column(Integer, ForeignKey('movies.id'))

    movie = relationship('Movie', back_populates='ratings')


class Genre(Base):
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True)
    name = Column(String)
