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
from sqlalchemy.orm import Session, joinedload
from contextlib import asynccontextmanager
from typing import List, Any
import sys
import os

# Add paths for both frozen and source mode
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = sys._MEIPASS
    backend_path = os.path.join(application_path, 'backend')
else:
    # Running as script
    backend_path = os.path.dirname(os.path.abspath(__file__))
    application_path = os.path.dirname(backend_path)

# Add paths
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
if application_path not in sys.path:
    sys.path.insert(0, application_path)

# Import database module
try:
    from backend.database import SessionLocal, init_db
    from backend.models import Movie, Series, Season, Episode
    from backend.recommender import recommend_movies, continue_series
    from backend.scan_endpoint import router as scan_router
    from backend.auth import router as auth_router
except ImportError:
    # Fallback to relative imports (when in backend directory)
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
        try:
            from backend.auth import User, hash_password
        except ImportError:
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
# HEALTH/STATUS ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    """Root endpoint - API status check."""
    return {"status": "online", "api": "MovieFlix Backend", "version": "2.0"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "movieflix-backend"}


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


@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    """
    Remove a movie from the library.
    
    Note: This only removes the database entry, not the actual file.
    
    Args:
        movie_id: ID of the movie to remove
        db: Database session
        
    Returns:
        dict: Status message with deleted movie info
        
    Raises:
        HTTPException: If movie not found
    """
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(404, "Movie not found")
    
    title = movie.title
    db.delete(movie)
    db.commit()
    
    return {
        "status": "deleted",
        "title": title,
        "message": f"'{title}' has been removed from your library"
    }


@app.post("/movies/bulk_add")
def bulk_add_movies(movies: list[dict], fetch_metadata: bool = True, db: Session = Depends(get_db)):
    """
    Bulk add movies to the database.
    
    Args:
        movies: List of movie dicts with 'title' and 'path'
        fetch_metadata: Whether to fetch TMDB metadata
        db: Database session
        
    Returns:
        dict: {added: int, skipped: int, updated: int}
    """
    from backend.metadata import fetch_movie_metadata
    
    added = 0
    skipped = 0
    updated = 0
    
    for movie_data in movies:
        title = movie_data.get('title')
        path = movie_data.get('path')
        
        if not title or not path:
            skipped += 1
            continue
        
        # Check if already exists
        existing = db.query(Movie).filter(Movie.path == path).first()
        if existing:
            skipped += 1
            continue
        
        # Create new movie
        new_movie = Movie(
            title=title,
            path=path,
            watched=False,
            last_position=0
        )
        
        # Fetch metadata if requested
        if fetch_metadata:
            try:
                metadata = fetch_movie_metadata(title)
                if metadata:
                    new_movie.poster = metadata.get('poster_path')
                    new_movie.rating = metadata.get('vote_average')
                    new_movie.overview = metadata.get('overview')
            except:
                pass  # Continue without metadata
        
        db.add(new_movie)
        added += 1
    
    db.commit()
    
    return {
        'added': added,
        'skipped': skipped,
        'updated': updated
    }


# ============================================================================
# TV SERIES ENDPOINTS
# ============================================================================

@app.get("/series")
def get_series(db: Session = Depends(get_db)):
    """
    Get all TV series in the library.
    
    Returns:
        list: List of all series objects with metadata including seasons and episodes
    """
    # Eager load seasons and episodes to include in response
    series_list = db.query(Series).options(
        joinedload(Series.seasons).joinedload(Season.episodes)
    ).all()
    
    # Convert to dict format with seasons included
    result = []
    for series in series_list:
        series_dict = {
            'id': series.id,
            'title': series.title,
            'overview': series.overview,
            'poster': series.poster,
            'seasons': [
                {
                    'id': season.id,
                    'season_number': season.season_number,
                    'episodes': [
                        {
                            'id': ep.id,
                            'title': ep.title,
                            'episode_number': ep.episode_number,
                            'path': ep.path,
                            'watched': ep.watched,
                            'last_position': ep.last_position
                        }
                        for ep in sorted(season.episodes, key=lambda e: e.episode_number)
                    ]
                }
                for season in sorted(series.seasons, key=lambda s: s.season_number)
            ]
        }
        result.append(series_dict)
    
    return result


@app.delete("/series/{series_id}")
def delete_series(series_id: int, db: Session = Depends(get_db)):
    """
    Remove a series from the library.
    
    Note: This removes the series and all its seasons/episodes from database,
    but does NOT delete the actual video files.
    
    Args:
        series_id: ID of the series to remove
        db: Database session
        
    Returns:
        dict: Status message with deleted series info
        
    Raises:
        HTTPException: If series not found
    """
    series = db.query(Series).filter(Series.id == series_id).first()
    if not series:
        raise HTTPException(404, "Series not found")
    
    title = series.title
    # Get episode count before deletion
    episode_count = sum(len(season.episodes) for season in series.seasons)
    
    # Delete series (cascade will delete seasons and episodes)
    db.delete(series)
    db.commit()
    
    return {
        "status": "deleted",
        "title": title,
        "episodes_removed": episode_count,
        "message": f"'{title}' and {episode_count} episodes have been removed from your library"
    }


@app.post("/series/bulk_add")
def bulk_add_series(series_list: List[Any], fetch_metadata: bool = True, db: Session = Depends(get_db)):
    """
    Bulk add TV series with episodes to the database.
    
    Args:
        series_list: List of series, where each series is a list of episode dicts
                    [[ep1, ep2, ...], [ep1, ep2, ...]]
        fetch_metadata: Whether to fetch TMDB metadata
        db: Database session
        
    Returns:
        dict: {added: int, skipped: int, episodes_added: int}
    """
    from backend.metadata import fetch_series_metadata
    
    added = 0
    skipped = 0
    episodes_added = 0
    errors = []
    
    for series_data in series_list:
        try:
            # series_data is a list of episodes for one series
            if not series_data or not isinstance(series_data, list):
                skipped += 1
                continue
            
            # Get series title from first episode
            first_ep = series_data[0]
            series_title = first_ep.get('series_title')
            
            if not series_title:
                skipped += 1
                errors.append(f"Missing series title in episode data")
                continue
            
            # Check if series already exists
            existing_series = db.query(Series).filter(Series.title == series_title).first()
            
            if existing_series:
                # Series exists, just add new episodes
                series = existing_series
            else:
                # Create new series
                series = Series(title=series_title)
                
                # Fetch metadata if requested
                if fetch_metadata:
                    try:
                        metadata = fetch_series_metadata(series_title)
                        if metadata:
                            series.poster = metadata.get('poster_path')
                            series.overview = metadata.get('overview')
                    except:
                        pass
                
                db.add(series)
                db.flush()  # Get series ID
                added += 1
            
            # Group episodes by season
            seasons_dict = {}
            for ep_data in series_data:
                season_num = ep_data.get('season_number', 1)
                if season_num not in seasons_dict:
                    seasons_dict[season_num] = []
                seasons_dict[season_num].append(ep_data)
            
            # Add seasons and episodes
            for season_num, episodes in seasons_dict.items():
                # Check if season exists
                season = db.query(Season).filter(
                    Season.series_id == series.id,
                    Season.season_number == season_num
                ).first()
                
                if not season:
                    season = Season(
                        series_id=series.id,
                        season_number=season_num
                    )
                    db.add(season)
                    db.flush()
                
                # Add episodes
                for ep_data in episodes:
                    ep_path = ep_data.get('path')
                    ep_num = ep_data.get('episode_number', 1)
                    ep_title = ep_data.get('title', f"Episode {ep_num}")
                    
                    # Check if episode exists
                    existing_ep = db.query(Episode).filter(Episode.path == ep_path).first()
                    if existing_ep:
                        continue
                    
                    episode = Episode(
                        title=ep_title,
                        episode_number=ep_num,
                        path=ep_path,
                        season_id=season.id,
                        watched=False,
                        last_position=0
                    )
                    db.add(episode)
                    episodes_added += 1
        
        except Exception as e:
            errors.append(f"Error processing series: {str(e)}")
            print(f"❌ Error adding series: {e}")
            import traceback
            traceback.print_exc()
    
    db.commit()
    
    return {
        'added': added,
        'skipped': skipped,
        'episodes_added': episodes_added,
        'errors': errors
    }


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
