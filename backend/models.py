from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    overview = Column(String, nullable=True)
    rating = Column(Float, nullable=True)
    poster = Column(String, nullable=True)
    path = Column(String, unique=True, nullable=False)
    watched = Column(Boolean, default=False)
    last_position = Column(Integer, default=0)


class Series(Base):
    __tablename__ = "series"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    overview = Column(String, nullable=True)
    poster = Column(String, nullable=True)
    seasons = relationship("Season", back_populates="series", cascade="all, delete-orphan")


class Season(Base):
    __tablename__ = "seasons"

    id = Column(Integer, primary_key=True)
    season_number = Column(Integer, nullable=False)
    series_id = Column(Integer, ForeignKey("series.id"), nullable=False)
    series = relationship("Series", back_populates="seasons")
    episodes = relationship("Episode", back_populates="season", cascade="all, delete-orphan")


class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=True)
    episode_number = Column(Integer, nullable=False)
    path = Column(String, unique=True, nullable=False)
    watched = Column(Boolean, default=False)
    last_position = Column(Integer, default=0)
    season_id = Column(Integer, ForeignKey("seasons.id"), nullable=False)
    season = relationship("Season", back_populates="episodes")
