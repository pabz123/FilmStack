from sqlalchemy.orm import Session
from backend.models import Movie, Episode


def recommend_movies(db, limit=10):
    return (
        db.query(Movie)
        .filter(Movie.watched == False)
        .order_by(Movie.rating.desc())
        .limit(limit)
        .all()
    )


def continue_series(db, limit=10):
    return (
        db.query(Episode)
        .filter(Episode.watched == False)
        .limit(limit)
        .all()
    )
