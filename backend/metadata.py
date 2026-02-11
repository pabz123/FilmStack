import requests
import os
import sys

# Load environment variables properly
try:
    from dotenv import load_dotenv
    # Load from parent directory
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(env_path)
    print(f"Loading .env from: {env_path}")
except ImportError:
    print("Warning: python-dotenv not installed")

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"  # For posters

# Check if API key is set
if not TMDB_API_KEY or TMDB_API_KEY == "YOUR_API_KEY":
    print("=" * 60)
    print("WARNING: TMDB API Key not configured!")
    print("Metadata fetching will not work.")
    print("Get your free API key from: https://www.themoviedb.org/settings/api")
    print("Add it to the .env file as: TMDB_API_KEY=your_key_here")
    print("=" * 60)


def fetch_movie_metadata(title, retries=3):
    """Fetch movie metadata with poster URL (with retry logic)"""
    if not TMDB_API_KEY or TMDB_API_KEY == "YOUR_API_KEY":
        return None
    
    for attempt in range(retries):
        try:
            r = requests.get(
                f"{BASE_URL}/search/movie",
                params={"api_key": TMDB_API_KEY, "query": title},
                timeout=10
            )
            r.raise_for_status()
            data = r.json()
            
            if data.get("results") and len(data["results"]) > 0:
                result = data["results"][0]
                
                # Add full poster URL
                if result.get("poster_path"):
                    result["poster_url"] = f"{IMAGE_BASE_URL}{result['poster_path']}"
                else:
                    result["poster_url"] = None
                
                # Add backdrop URL
                if result.get("backdrop_path"):
                    result["backdrop_url"] = f"https://image.tmdb.org/t/p/w1280{result['backdrop_path']}"
                else:
                    result["backdrop_url"] = None
                
                return result
            else:
                return None
        except requests.exceptions.Timeout:
            if attempt < retries - 1:
                continue
            return None
        except Exception as e:
            if attempt < retries - 1:
                continue
            return None
    
    return None


def fetch_series_metadata(title):
    """Fetch TV series metadata with poster URL"""
    if not TMDB_API_KEY or TMDB_API_KEY == "YOUR_API_KEY":
        print(f"Skipping metadata for '{title}' - No API key")
        return None
    
    try:
        print(f"Fetching metadata for series: {title}")
        r = requests.get(
            f"{BASE_URL}/search/tv",
            params={"api_key": TMDB_API_KEY, "query": title},
            timeout=10
        )
        r.raise_for_status()
        data = r.json()
        
        if data.get("results") and len(data["results"]) > 0:
            result = data["results"][0]
            
            # Add full poster URL
            if result.get("poster_path"):
                result["poster_url"] = f"{IMAGE_BASE_URL}{result['poster_path']}"
            else:
                result["poster_url"] = None
            
            # Add backdrop URL
            if result.get("backdrop_path"):
                result["backdrop_url"] = f"https://image.tmdb.org/t/p/w1280{result['backdrop_path']}"
            else:
                result["backdrop_url"] = None
            
            print(f"  ✓ Found metadata for: {title}")
            if result.get("poster_url"):
                print(f"    Poster: {result['poster_url']}")
            
            return result
        else:
            print(f"  ✗ No metadata found for: {title}")
            return None
    except Exception as e:
        print(f"Error fetching series metadata for '{title}': {str(e)}")
        return None


def fetch_movie_cast(tmdb_id):
    """
    Fetch cast and crew information for a movie from TMDB.
    
    Args:
        tmdb_id (int): TMDB movie ID
        
    Returns:
        dict: {
            'cast': [{'name': str, 'character': str, 'profile_path': str}, ...],
            'director': str,
            'writers': [str, ...]
        }
    """
    if not TMDB_API_KEY or TMDB_API_KEY == "YOUR_API_KEY":
        print("Skipping cast fetch - No API key")
        return None
    
    try:
        print(f"Fetching cast for movie ID: {tmdb_id}")
        r = requests.get(
            f"{BASE_URL}/movie/{tmdb_id}/credits",
            params={"api_key": TMDB_API_KEY},
            timeout=10
        )
        r.raise_for_status()
        data = r.json()
        
        # Get top 10 cast members
        cast = []
        for person in data.get("cast", [])[:10]:
            cast.append({
                'name': person.get('name'),
                'character': person.get('character'),
                'profile_path': person.get('profile_path'),
                'profile_url': f"{IMAGE_BASE_URL}{person['profile_path']}" if person.get('profile_path') else None
            })
        
        # Get director
        director = None
        for crew in data.get("crew", []):
            if crew.get('job') == 'Director':
                director = crew.get('name')
                break
        
        # Get writers
        writers = []
        for crew in data.get("crew", []):
            if crew.get('job') in ['Writer', 'Screenplay', 'Story']:
                writers.append(crew.get('name'))
        
        print(f"  ✓ Found {len(cast)} cast members")
        
        return {
            'cast': cast,
            'director': director,
            'writers': list(set(writers))[:3]  # Top 3 unique writers
        }
        
    except Exception as e:
        print(f"Error fetching cast: {str(e)}")
        return None


def fetch_series_cast(tmdb_id):
    """
    Fetch cast and crew information for a TV series from TMDB.
    
    Args:
        tmdb_id (int): TMDB series ID
        
    Returns:
        dict: {
            'cast': [{'name': str, 'character': str, 'profile_url': str}, ...],
            'creators': [str, ...]
        }
    """
    if not TMDB_API_KEY or TMDB_API_KEY == "YOUR_API_KEY":
        print("Skipping cast fetch - No API key")
        return None
    
    try:
        print(f"Fetching cast for series ID: {tmdb_id}")
        r = requests.get(
            f"{BASE_URL}/tv/{tmdb_id}/credits",
            params={"api_key": TMDB_API_KEY},
            timeout=10
        )
        r.raise_for_status()
        data = r.json()
        
        # Get top 10 cast members
        cast = []
        for person in data.get("cast", [])[:10]:
            cast.append({
                'name': person.get('name'),
                'character': person.get('character'),
                'profile_path': person.get('profile_path'),
                'profile_url': f"{IMAGE_BASE_URL}{person['profile_path']}" if person.get('profile_path') else None
            })
        
        # Get creators from main series info
        r2 = requests.get(
            f"{BASE_URL}/tv/{tmdb_id}",
            params={"api_key": TMDB_API_KEY},
            timeout=10
        )
        series_data = r2.json()
        creators = [creator.get('name') for creator in series_data.get('created_by', [])]
        
        print(f"  ✓ Found {len(cast)} cast members")
        
        return {
            'cast': cast,
            'creators': creators
        }
        
    except Exception as e:
        print(f"Error fetching series cast: {str(e)}")
        return None
