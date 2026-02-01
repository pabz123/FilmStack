"""
Library scanner endpoint - scans library folders and adds to database
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from database import SessionLocal
from models import Movie, Series, Season, Episode
from scanner import scan_movies, scan_series
from metadata import fetch_movie_metadata, fetch_series_metadata

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/scan")
def scan_library(db: Session = Depends(get_db)):
    """Scan library folders and add content to database"""
    
    results = {
        "movies_added": 0,
        "series_added": 0,
        "episodes_added": 0,
        "errors": []
    }
    
    # Get library paths
    library_path = os.path.join(os.path.dirname(current_dir), "library")
    movies_path = os.path.join(library_path, "mo")
    series_path = os.path.join(library_path, "se")
    
    print(f"Scanning library at: {library_path}")
    print(f"Movies path: {movies_path}")
    print(f"Series path: {series_path}")
    
    # Scan movies
    if os.path.exists(movies_path):
        try:
            print("\n=== Scanning Movies ===")
            movies_data = scan_movies(movies_path)
            print(f"Found {len(movies_data)} movie files")
            
            for movie_data in movies_data:
                # Check if already exists
                existing = db.query(Movie).filter(Movie.path == movie_data["path"]).first()
                if existing:
                    print(f"Skipping existing movie: {movie_data['title']}")
                    continue
                
                # Fetch metadata
                print(f"Processing movie: {movie_data['title']}")
                metadata = fetch_movie_metadata(movie_data["title"])
                
                # Create movie
                movie = Movie(
                    title=movie_data["title"],
                    path=movie_data["path"],
                    overview=metadata.get("overview") if metadata else None,
                    rating=metadata.get("vote_average") if metadata else None,
                    poster=metadata.get("poster_url") if metadata else None  # Full URL now
                )
                db.add(movie)
                results["movies_added"] += 1
                print(f"  ✓ Added: {movie_data['title']}")
                if metadata and metadata.get("poster_url"):
                    print(f"    Poster: {metadata['poster_url'][:50]}...")
            
            db.commit()
            print(f"Movies scan complete: {results['movies_added']} added")
        except Exception as e:
            error_msg = f"Movies scan error: {str(e)}"
            print(error_msg)
            results["errors"].append(error_msg)
            import traceback
            traceback.print_exc()
    else:
        print(f"Movies path does not exist: {movies_path}")
    
    # Scan series
    if os.path.exists(series_path):
        try:
            print("\n=== Scanning Series ===")
            series_data = scan_series(series_path)
            print(f"Found {len(series_data)} episode files")
            
            # Group by series
            series_dict = {}
            for ep_data in series_data:
                series_title = ep_data["series_title"]
                if series_title not in series_dict:
                    series_dict[series_title] = {}
                
                season_num = ep_data["season_number"]
                if season_num not in series_dict[series_title]:
                    series_dict[series_title][season_num] = []
                
                series_dict[series_title][season_num].append(ep_data)
            
            print(f"Grouped into {len(series_dict)} series")
            
            # Add to database
            for series_title, seasons in series_dict.items():
                print(f"\nProcessing series: {series_title}")
                
                # Check if series exists
                series_obj = db.query(Series).filter(Series.title == series_title).first()
                
                if not series_obj:
                    # Fetch metadata
                    metadata = fetch_series_metadata(series_title)
                    
                    series_obj = Series(
                        title=series_title,
                        overview=metadata.get("overview") if metadata else None,
                        poster=metadata.get("poster_url") if metadata else None  # Full URL now
                    )
                    db.add(series_obj)
                    db.flush()
                    results["series_added"] += 1
                    print(f"  ✓ Added series: {series_title}")
                    if metadata and metadata.get("poster_url"):
                        print(f"    Poster: {metadata['poster_url'][:50]}...")
                else:
                    print(f"  Series already exists: {series_title}")
                
                # Add seasons and episodes
                for season_num, episodes in seasons.items():
                    print(f"  Processing Season {season_num} ({len(episodes)} episodes)")
                    
                    # Check if season exists
                    season_obj = db.query(Season).filter(
                        Season.series_id == series_obj.id,
                        Season.season_number == season_num
                    ).first()
                    
                    if not season_obj:
                        season_obj = Season(
                            series_id=series_obj.id,
                            season_number=season_num
                        )
                        db.add(season_obj)
                        db.flush()
                        print(f"    Added Season {season_num}")
                    
                    # Add episodes
                    for ep_data in episodes:
                        existing_ep = db.query(Episode).filter(
                            Episode.path == ep_data["path"]
                        ).first()
                        
                        if not existing_ep:
                            episode = Episode(
                                season_id=season_obj.id,
                                episode_number=ep_data["episode_number"],
                                path=ep_data["path"],
                                title=f"Episode {ep_data['episode_number']}"
                            )
                            db.add(episode)
                            results["episodes_added"] += 1
                            print(f"      Added E{ep_data['episode_number']:02d}")
            
            db.commit()
            print(f"\nSeries scan complete:")
            print(f"  Series added: {results['series_added']}")
            print(f"  Episodes added: {results['episodes_added']}")
        except Exception as e:
            error_msg = f"Series scan error: {str(e)}"
            print(error_msg)
            results["errors"].append(error_msg)
            import traceback
            traceback.print_exc()
    else:
        print(f"Series path does not exist: {series_path}")
    
    print("\n=== Scan Complete ===")
    print(f"Results: {results}")
    return results


@router.post("/scan_folder")
def scan_folder(data: dict, db: Session = Depends(get_db)):
    """Scan a specific folder and add to library"""
    folder_path = data.get("path")
    content_type = data.get("type", "movies")  # "movies" or "series"
    
    if not folder_path or not os.path.exists(folder_path):
        raise HTTPException(status_code=400, detail="Invalid folder path")
    
    results = {"added": 0, "errors": []}
    
    try:
        if content_type == "movies":
            movies_data = scan_movies(folder_path)
            
            for movie_data in movies_data:
                # Check if already exists
                existing = db.query(Movie).filter(Movie.path == movie_data["path"]).first()
                if existing:
                    continue
                
                # Fetch metadata
                metadata = fetch_movie_metadata(movie_data["title"])
                
                # Create movie
                movie = Movie(
                    title=movie_data["title"],
                    path=movie_data["path"],
                    overview=metadata.get("overview") if metadata else None,
                    rating=metadata.get("vote_average") if metadata else None,
                    poster=metadata.get("poster_url") if metadata else None
                )
                db.add(movie)
                results["added"] += 1
            
            db.commit()
            
        elif content_type == "series":
            series_data = scan_series(folder_path)
            
            # Group by series
            series_dict = {}
            for ep_data in series_data:
                series_title = ep_data["series_title"]
                if series_title not in series_dict:
                    series_dict[series_title] = {}
                
                season_num = ep_data["season_number"]
                if season_num not in series_dict[series_title]:
                    series_dict[series_title][season_num] = []
                
                series_dict[series_title][season_num].append(ep_data)
            
            # Add to database
            for series_title, seasons in series_dict.items():
                series_obj = db.query(Series).filter(Series.title == series_title).first()
                
                if not series_obj:
                    metadata = fetch_series_metadata(series_title)
                    
                    series_obj = Series(
                        title=series_title,
                        overview=metadata.get("overview") if metadata else None,
                        poster=metadata.get("poster_url") if metadata else None
                    )
                    db.add(series_obj)
                    db.flush()
                    results["added"] += 1
                
                # Add seasons and episodes
                for season_num, episodes in seasons.items():
                    season_obj = db.query(Season).filter(
                        Season.series_id == series_obj.id,
                        Season.season_number == season_num
                    ).first()
                    
                    if not season_obj:
                        season_obj = Season(
                            series_id=series_obj.id,
                            season_number=season_num
                        )
                        db.add(season_obj)
                        db.flush()
                    
                    # Add episodes
                    for ep_data in episodes:
                        existing_ep = db.query(Episode).filter(
                            Episode.path == ep_data["path"]
                        ).first()
                        
                        if not existing_ep:
                            episode = Episode(
                                season_id=season_obj.id,
                                episode_number=ep_data["episode_number"],
                                path=ep_data["path"],
                                title=f"Episode {ep_data['episode_number']}"
                            )
                            db.add(episode)
            
            db.commit()
        
        return results
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
