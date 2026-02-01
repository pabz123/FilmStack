"""
Fetch TMDB Metadata for Movies in Database
Updates poster and rating information for existing movies
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import Movie
from backend.tmdb_notifier import TMDBNotifier
from dotenv import load_dotenv
import re

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')

def clean_title(title):
    """Clean movie title for better TMDB matching"""
    # Remove common patterns
    patterns = [
        r'\(NKIRI\.COM\)',
        r'\.DOWNLOADED\.FROM\.NKIRI\.COM',
        r'\(Awafim\.tv\)',
        r'\.\d{4}\.',  # Year in dots
        r'\.WEB-DL',
        r'\.BluRay',
        r'\.HDTV',
        r'\.DVDRip',
        r'\.BRRip',
        r'\.\w+\.\w+$',  # File extensions
    ]
    
    clean = title
    for pattern in patterns:
        clean = re.sub(pattern, ' ', clean, flags=re.IGNORECASE)
    
    # Replace dots with spaces
    clean = clean.replace('.', ' ')
    
    # Remove extra spaces
    clean = ' '.join(clean.split())
    
    # Extract year if present
    year_match = re.search(r'\b(19|20)\d{2}\b', clean)
    year = year_match.group(0) if year_match else None
    
    # Remove year from title for search
    if year:
        clean = clean.replace(year, '').strip()
    
    return clean, year

def search_tmdb_movie(notifier, title, year=None):
    """Search TMDB for a movie"""
    try:
        params = {
            "api_key": notifier.api_key,
            "language": "en-US",
            "query": title,
            "include_adult": "false"
        }
        
        if year:
            params["year"] = year
        
        import requests
        response = requests.get(
            f"{notifier.base_url}/search/movie",
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            if results:
                return results[0]  # Return best match
        
        return None
    except Exception as e:
        print(f"  Error searching TMDB: {e}")
        return None

def update_movie_metadata():
    """Update metadata for all movies in database"""
    if not TMDB_API_KEY or TMDB_API_KEY == "YOUR_API_KEY":
        print("❌ Error: TMDB_API_KEY not set in .env file")
        print("Get a free API key from https://www.themoviedb.org/settings/api")
        return
    
    print("=" * 70)
    print("TMDB Metadata Updater for MovieFlix")
    print("=" * 70)
    print()
    
    notifier = TMDBNotifier(TMDB_API_KEY)
    db = SessionLocal()
    
    try:
        movies = db.query(Movie).all()
        print(f"Found {len(movies)} movies in database")
        print()
        
        updated_count = 0
        failed_count = 0
        
        for i, movie in enumerate(movies, 1):
            print(f"[{i}/{len(movies)}] {movie.title}")
            
            # Skip if already has poster and rating
            if movie.poster and movie.rating:
                print(f"  ✓ Already has metadata (Rating: {movie.rating})")
                updated_count += 1
                continue
            
            # Clean title and search TMDB
            clean_title_str, year = clean_title(movie.title)
            print(f"  Searching TMDB for: '{clean_title_str}' ({year or 'no year'})")
            
            tmdb_data = search_tmdb_movie(notifier, clean_title_str, year)
            
            if tmdb_data:
                # Update movie with TMDB data
                if tmdb_data.get('poster_path'):
                    movie.poster = tmdb_data['poster_path']  # Store path, not full URL
                    print(f"  ✓ Updated poster")
                
                if tmdb_data.get('vote_average'):
                    movie.rating = tmdb_data['vote_average']
                    print(f"  ✓ Updated rating: {movie.rating}")
                
                if tmdb_data.get('overview') and not movie.overview:
                    movie.overview = tmdb_data['overview']
                    print(f"  ✓ Updated overview")
                
                db.commit()
                updated_count += 1
                print(f"  ✓ Updated successfully")
            else:
                print(f"  ⚠️  No TMDB match found")
                failed_count += 1
            
            print()
        
        print("=" * 70)
        print(f"✓ Complete!")
        print(f"  Updated: {updated_count}/{len(movies)} movies")
        print(f"  Failed: {failed_count}/{len(movies)} movies")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    update_movie_metadata()
