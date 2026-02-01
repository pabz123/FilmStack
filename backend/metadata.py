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


def fetch_movie_metadata(title):
    """Fetch movie metadata with poster URL"""
    if not TMDB_API_KEY or TMDB_API_KEY == "YOUR_API_KEY":
        print(f"Skipping metadata for '{title}' - No API key")
        return None
    
    try:
        print(f"Fetching metadata for movie: {title}")
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
            
            print(f"  ✓ Found metadata for: {title}")
            if result.get("poster_url"):
                print(f"    Poster: {result['poster_url']}")
            
            return result
        else:
            print(f"  ✗ No metadata found for: {title}")
            return None
    except Exception as e:
        print(f"Error fetching movie metadata for '{title}': {str(e)}")
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
