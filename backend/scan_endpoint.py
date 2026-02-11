"""
Library scanner endpoint - scans library folders and adds to database
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from backend.database import SessionLocal
from backend.models import Movie, Series, Season, Episode
from backend.scanner import scan_movies, scan_series
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
    """Scan entire PC for movies and series (20+ minutes)"""
    
    results = {
        "movies_added": 0,
        "series_added": 0,
        "episodes_added": 0,
        "errors": [],
        "drives_scanned": []
    }
    
    print("\n" + "="*50)
    print("Starting Full PC Scan")
    print("Looking for videos 20+ minutes")
    print("="*50 + "\n")
    
    # Import scanner functions
    from backend.scanner import get_all_drives, scan_movies, scan_series
    
    # Get all available drives
    drives = get_all_drives()
    print(f"Found drives: {', '.join(drives)}")
    
    all_movies = []
    all_series = {}
    
    # Scan each drive
    for drive in drives:
        try:
            print(f"\n📀 Scanning drive: {drive}")
            results["drives_scanned"].append(drive)
            
            # Scan for movies
            movies_data = scan_movies(drive)
            all_movies.extend(movies_data)
            print(f"  ✓ Found {len(movies_data)} movies on {drive}")
            
            # Scan for series
            series_data = scan_series(drive)
            # Merge series data
            for series_title, episodes in series_data.items():
                if series_title in all_series:
                    all_series[series_title].extend(episodes)
                else:
                    all_series[series_title] = episodes
            print(f"  ✓ Found {len(series_data)} series on {drive}")
            
        except PermissionError as e:
            error_msg = f"Permission denied for {drive}: {str(e)}"
            print(f"  ⚠️  {error_msg}")
            results["errors"].append(error_msg)
        except Exception as e:
            error_msg = f"Error scanning {drive}: {str(e)}"
            print(f"  ❌ {error_msg}")
            results["errors"].append(error_msg)
    
    print(f"\n📊 Scan Complete:")
    print(f"  Total movies found: {len(all_movies)}")
    print(f"  Total series found: {len(all_series)}")
    
    # Process movies
    print("\n" + "="*50)
    print("Adding Movies to Database")
    print("="*50)
    
    for movie_data in all_movies:
        try:
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
            results["movies_added"] += 1
            
            if results["movies_added"] % 10 == 0:
                print(f"  Added {results['movies_added']} movies...")
                
        except Exception as e:
            error_msg = f"Error adding movie {movie_data['title']}: {str(e)}"
            results["errors"].append(error_msg)
    
    # Commit movies
    try:
        db.commit()
        print(f"✓ Added {results['movies_added']} movies to database")
    except Exception as e:
        db.rollback()
        print(f"❌ Error committing movies: {e}")
    
    # Process series
    print("\n" + "="*50)
    print("Adding Series to Database")
    print("="*50)
    
    for series_title, episodes_list in all_series.items():
        try:
            # Check if series exists
            series_obj = db.query(Series).filter(Series.title == series_title).first()
            
            if not series_obj:
                # Fetch metadata
                metadata = fetch_series_metadata(series_title)
                
                series_obj = Series(
                    title=series_title,
                    overview=metadata.get("overview") if metadata else None,
                    poster=metadata.get("poster_url") if metadata else None
                )
                db.add(series_obj)
                db.flush()
                results["series_added"] += 1
            
            # Group episodes by season
            seasons_dict = {}
            for ep_data in episodes_list:
                season_num = ep_data["season_number"]
                if season_num not in seasons_dict:
                    seasons_dict[season_num] = []
                seasons_dict[season_num].append(ep_data)
            
            # Add seasons and episodes
            for season_num, episodes in seasons_dict.items():
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
                        
        except Exception as e:
            error_msg = f"Error processing series {series_title}: {str(e)}"
            results["errors"].append(error_msg)
    
    # Commit series
    try:
        db.commit()
        print(f"✓ Added {results['series_added']} series, {results['episodes_added']} episodes")
    except Exception as e:
        db.rollback()
        print(f"❌ Error committing series: {e}")
    
    print("\n" + "="*50)
    print("Scan Summary")
    print("="*50)
    print(f"Drives scanned: {', '.join(results['drives_scanned'])}")
    print(f"Movies added: {results['movies_added']}")
    print(f"Series added: {results['series_added']}")
    print(f"Episodes added: {results['episodes_added']}")
    print(f"Errors: {len(results['errors'])}")
    print("="*50 + "\n")
    
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
