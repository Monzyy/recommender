from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    summary = Column(String)
    budget = Column(Integer)
    # TODO: Add more attributes

    ratings = relationship('Rating', back_populates='movie', cascade='all, delete-orphan')


class Rating(Base):
    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    rating = Column(Float)
    created_at = Column(DateTime)
    movie_id = Column(Integer, ForeignKey('movies.id'))

    movie = relationship('Movie', back_populates='ratings')
