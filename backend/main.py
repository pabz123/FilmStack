"""
MovieFlix Backend API Server
=============================

This is the main FastAPI application that provides the backend API for MovieFlix.
It handles:
- Database initialization and management
- User authentication
- Movie and series data endpoints
- TMDB integration for metadata and trending content
- Recommendation engine
- Watch history tracking

Dependencies:
- FastAPI: Web framework
- SQLAlchemy: Database ORM
- TMDB: Movie metadata API

Environment Variables (from .env):
- TMDB_API_KEY: API key for The Movie Database
- API_HOST: Host to bind the server (default: 127.0.0.1)
- API_PORT: Port to run the server (default: 8765)

Usage:
    python backend/main.py
    or
    start_backend.bat (Windows)

API Documentation:
    Once running, visit http://127.0.0.1:8765/docs for interactive API docs
"""

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import database module
from database import SessionLocal, init_db
from models import Movie, Series, Season, Episode
from recommender import recommend_movies, continue_series
from scan_endpoint import router as scan_router
from auth import router as auth_router


# Lifespan handler for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events:
    - Startup: Initialize database, create default admin user if needed
    - Shutdown: Cleanup resources
    
    Args:
        app: FastAPI application instance
    """
    # Startup
    print("=" * 50)
    print("Initializing database...")
    try:
        init_db()
        print("Database initialized successfully!")
        
        # Create default admin user if no users exist
        from auth import User, hash_password
        db = SessionLocal()
        try:
            user_count = db.query(User).count()
            if user_count == 0:
                admin_user = User(
                    username="admin",
                    password_hash=hash_password("admin123"),
                    is_admin=1
                )
                db.add(admin_user)
                db.commit()
                print("Created default admin user (username: admin, password: admin123)")
                print("⚠️  CHANGE THIS PASSWORD IMMEDIATELY!")
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error initializing database: {e}")
        import traceback
        traceback.print_exc()
    print("=" * 50)
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(title="Local Streaming Library", lifespan=lifespan)

# Include routers
app.include_router(scan_router, prefix="/library", tags=["library"])
app.include_router(auth_router, prefix="/auth", tags=["authentication"])


# Dependency for database sessions
def get_db():
    """
    Database session dependency.
    
    Creates a new database session for each request and closes it after use.
    This ensures proper connection management and prevents memory leaks.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# MOVIE ENDPOINTS
# ============================================================================

@app.get("/movies")
def get_movies(db: Session = Depends(get_db)):
    """
    Get all movies in the library.
    
    Returns:
        list: List of all movie objects with metadata
    """
    return db.query(Movie).all()


@app.patch("/movies/{movie_id}/metadata")
def update_movie_metadata(movie_id: int, metadata: dict, db: Session = Depends(get_db)):
    """
    Update movie metadata (poster, rating, overview).
    
    Args:
        movie_id: ID of the movie
        metadata: Dictionary with poster, rating, and/or overview
        db: Database session
        
    Returns:
        dict: Updated movie data
    """
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(404, "Movie not found")
    
    # Update fields if provided
    if 'poster' in metadata:
        movie.poster = metadata['poster']
    if 'rating' in metadata:
        movie.rating = metadata['rating']
    if 'overview' in metadata:
        movie.overview = metadata['overview']
    
    db.commit()
    db.refresh(movie)
    
    return movie


@app.post("/movies/{movie_id}/watch")
def watch_movie(movie_id: int, db: Session = Depends(get_db)):
    """
    Mark a movie as watched.
    
    Args:
        movie_id: ID of the movie to mark as watched
        db: Database session
        
    Returns:
        dict: Status message
        
    Raises:
        HTTPException: If movie not found
    """
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(404, "Movie not found")
    movie.watched = True
    db.commit()
    return {"status": "watched"}


# ============================================================================
# TV SERIES ENDPOINTS
# ============================================================================

@app.get("/series")
def get_series(db: Session = Depends(get_db)):
    """
    Get all TV series in the library.
    
    Returns:
        list: List of all series objects with metadata
    """
    return db.query(Series).all()

@app.patch("/series/{series_id}/metadata")
def update_series_metadata(series_id: int, metadata: dict, db: Session = Depends(get_db)):
    """
    Update series metadata (poster, overview).
    
    Args:
        series_id: ID of the series
        metadata: Dictionary with poster and/or overview
        db: Database session
        
    Returns:
        dict: Updated series data
    """
    series = db.query(Series).filter(Series.id == series_id).first()
    if not series:
        raise HTTPException(404, "Series not found")
    
    if 'poster' in metadata:
        series.poster = metadata['poster']
    if 'overview' in metadata:
        series.overview = metadata['overview']
    
    db.commit()
    db.refresh(series)
    
    return series

@app.get("/series/{series_id}/seasons")
def get_seasons(series_id: int, db: Session = Depends(get_db)):
    series = db.query(Series).filter(Series.id == series_id).first()
    if not series:
        raise HTTPException(404, "Series not found")
    return series.seasons

@app.get("/seasons/{season_id}/episodes")
def get_episodes(season_id: int, db: Session = Depends(get_db)):
    season = db.query(Season).filter(Season.id == season_id).first()
    if not season:
        raise HTTPException(404, "Season not found")
    return season.episodes

@app.post("/episodes/{episode_id}/watch")
def watch_episode(episode_id: int, db: Session = Depends(get_db)):
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not episode:
        raise HTTPException(404, "Episode not found")
    episode.watched = True
    db.commit()
    return {"status": "watched"}

@app.get("/recommendations/movies")
def movie_recommendations(db: Session = Depends(get_db)):
    return recommend_movies(db)

@app.get("/recommendations/series")
def series_recommendations(db: Session = Depends(get_db)):
    return continue_series(db)

@app.post("/movies/{movie_id}/progress")
def save_movie_progress(movie_id: int, position: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(404, "Movie not found")

    movie.last_position = position
    db.commit()
    return {"status": "saved"}

@app.post("/episodes/{episode_id}/progress")
def save_episode_progress(episode_id: int, position: int, db: Session = Depends(get_db)):
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not episode:
        raise HTTPException(404, "Episode not found")

    episode.last_position = position
    db.commit()
    return {"status": "saved"}


# New releases and trending endpoints
@app.get("/tmdb/trending")
def get_trending():
    """Get trending movies and shows"""
    from tmdb_notifier import TMDBNotifier
    notifier = TMDBNotifier(os.getenv("TMDB_API_KEY", ""))
    return notifier.get_trending_today()


@app.get("/tmdb/new-releases")
def get_new_releases(days: int = 7):
    """Get new movie releases from last N days"""
    from tmdb_notifier import TMDBNotifier
    notifier = TMDBNotifier(os.getenv("TMDB_API_KEY", ""))
    return notifier.get_new_movies(days)


@app.get("/tmdb/upcoming")
def get_upcoming():
    """Get upcoming movie releases"""
    from tmdb_notifier import TMDBNotifier
    notifier = TMDBNotifier(os.getenv("TMDB_API_KEY", ""))
    return notifier.get_upcoming_movies()


@app.get("/tmdb/popular")
def get_popular(page: int = 1):
    """Get popular movies"""
    from tmdb_notifier import TMDBNotifier
    notifier = TMDBNotifier(os.getenv("TMDB_API_KEY", ""))
    return notifier.get_popular_movies(page)


# Get episodes by series ID
@app.get("/series/{series_id}/episodes")
def get_series_episodes(series_id: int, db: Session = Depends(get_db)):
    """Get all episodes for a series"""
    series = db.query(Series).filter(Series.id == series_id).first()
    if not series:
        raise HTTPException(404, "Series not found")
    
    all_episodes = []
    for season in series.seasons:
        for episode in season.episodes:
            all_episodes.append({
                "id": episode.id,
                "title": episode.title or f"Episode {episode.episode_number}",
                "episode_number": episode.episode_number,
                "season_number": season.season_number,
                "path": episode.path,
                "watched": episode.watched,
                "last_position": episode.last_position
            })
    
    return all_episodes


if __name__ == "__main__":
    import uvicorn
    import os
    
    # Load port from environment
    port = int(os.getenv("API_PORT", 8765))
    host = os.getenv("API_HOST", "127.0.0.1")
    
    print("=" * 50)
    print("Starting Movie Library Backend Server")
    print("=" * 50)
    print(f"API will be available at: http://{host}:{port}")
    print(f"API docs available at: http://{host}:{port}/docs")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    uvicorn.run(app, host=host, port=port)
