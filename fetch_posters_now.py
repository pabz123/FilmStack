"""
MovieFlix TMDB Poster Fetcher
===============================
Fetches movie posters and ratings from TMDB API.
No database imports required - uses REST API only!
"""
import sys
import os
from pathlib import Path
import requests
import re
import time
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')
API_URL = 'http://localhost:8765'

print("=" * 70)
print("  MovieFlix TMDB Poster Fetcher")
print("=" * 70)
print(f"TMDB API Key: {'✓ Found' if TMDB_API_KEY else '✗ MISSING!'}")
print(f"Backend URL: {API_URL}")
print("=" * 70)
print()


def clean_title(title):
    """Clean movie title for better TMDB matching"""
    # Remove common download site tags and quality markers
    patterns = [
        r'\(NKIRI\.COM\)',
        r'\.DOWNLOADED\.FROM\.NKIRI\.COM',
        r'\(Awafim\.tv\)',
        r'Awafim\.tv',
        r'NKIRI\.COM',
        r'\.WEB-DL',
        r'\.WEBRip',
        r'\.BluRay',
        r'\.BRRip',
        r'\.HDTV',
        r'\.DVDRip',
        r'\.HDRIP',
        r'\[.*?\]',  # Remove brackets
        r'\(.*?p\)',  # Remove (720p), (1080p), etc
        r'\d{3,4}p',  # Remove 720p, 1080p
        r'x264',
        r'x265',
        r'H\.264',
        r'H\.265',
        r'HEVC',
    ]
    
    clean = title
    for pattern in patterns:
        clean = re.sub(pattern, ' ', clean, flags=re.IGNORECASE)
    
    # Replace dots and underscores with spaces
    clean = clean.replace('.', ' ').replace('_', ' ')
    
    # Remove extra spaces
    clean = ' '.join(clean.split())
    
    return clean.strip()


def extract_year(title):
    """Extract year from title (looks for 4-digit year)"""
    year_match = re.search(r'\b(19\d{2}|20[0-2]\d)\b', title)
    if year_match:
        return year_match.group(0)
    return None


def search_tmdb(title, year=None):
    """Search TMDB for movie"""
    try:
        search_url = "https://api.themoviedb.org/3/search/movie"
        params = {
            'api_key': TMDB_API_KEY,
            'query': title,
        }
        
        if year:
            params['year'] = year
        
        response = requests.get(search_url, params=params, timeout=10)
        
        if response.status_code != 200:
            return None
        
        results = response.json().get('results', [])
        
        if results:
            return results[0]  # Return best match
        
        return None
        
    except Exception as e:
        print(f"      ✗ TMDB search error: {e}")
        return None


def main():
    """Main poster fetching function"""
    
    if not TMDB_API_KEY:
        print("❌ ERROR: TMDB_API_KEY not found in .env file!")
        print()
        print("Please add your TMDB API key to .env:")
        print("TMDB_API_KEY=your_key_here")
        print()
        return
    
    # Check if backend is running
    print("Step 1: Checking backend connection...")
    try:
        response = requests.get(f'{API_URL}/docs', timeout=2)
        print("✓ Backend is running")
    except:
        print("❌ Backend is NOT running!")
        print()
        print("Please start the backend first:")
        print("  cd D:\\movie_library")
        print("  python -m uvicorn backend.main:app --port 8765")
        print()
        return
    
    # Get all movies
    print()
    print("Step 2: Fetching movies from backend...")
    try:
        response = requests.get(f'{API_URL}/movies')
        if response.status_code != 200:
            print(f"❌ Failed to get movies: HTTP {response.status_code}")
            return
        
        all_movies = response.json()
        print(f"✓ Found {len(all_movies)} movies in library")
        
    except Exception as e:
        print(f"❌ Error fetching movies: {e}")
        return
    
    # Filter movies without posters
    movies_without_posters = [
        m for m in all_movies 
        if not m.get('poster_url') or not m['poster_url'].startswith('http')
    ]
    
    if not movies_without_posters:
        print()
        print("=" * 70)
        print("✅ All movies already have posters!")
        print("=" * 70)
        return
    
    print(f"✓ Found {len(movies_without_posters)} movies without posters")
    print()
    print("Step 3: Fetching posters from TMDB...")
    print("-" * 70)
    print()
    
    updated_count = 0
    failed_count = 0
    total = len(movies_without_posters)
    
    for i, movie in enumerate(movies_without_posters, 1):
        movie_id = movie['id']
        title = movie['title']
        
        print(f"[{i}/{total}] {title}")
        
        # Clean title
        clean = clean_title(title)
        year = extract_year(title)
        
        print(f"      Searching TMDB: '{clean}' ({year or 'no year'})")
        
        # Search TMDB
        tmdb_result = search_tmdb(clean, year)
        
        if tmdb_result:
            poster_path = tmdb_result.get('poster_path')
            rating = tmdb_result.get('vote_average', 0)
            tmdb_title = tmdb_result.get('title', '')
            
            print(f"      ✓ Found: {tmdb_title} (Rating: {rating:.1f}/10)")
            
            if poster_path:
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                
                # Update via API
                try:
                    update_response = requests.patch(
                        f'{API_URL}/movies/{movie_id}/metadata',
                        json={
                            'poster_url': poster_url,
                            'rating': float(rating)
                        }
                    )
                    
                    if update_response.status_code == 200:
                        print(f"      ✅ Poster updated successfully!")
                        updated_count += 1
                    else:
                        print(f"      ✗ Update failed: HTTP {update_response.status_code}")
                        failed_count += 1
                        
                except Exception as e:
                    print(f"      ✗ Update error: {e}")
                    failed_count += 1
            else:
                print(f"      ⚠️  No poster available on TMDB")
                failed_count += 1
        else:
            print(f"      ⚠️  Not found on TMDB")
            failed_count += 1
        
        # Rate limiting (be nice to TMDB)
        time.sleep(0.3)
        print()
    
    # Summary
    print("=" * 70)
    print("  ✅ FETCH COMPLETE!")
    print("=" * 70)
    print(f"  Updated: {updated_count}/{total} movies")
    print(f"  Failed:  {failed_count}/{total} movies")
    print("=" * 70)
    print()
    print("💡 Tip: Refresh your MovieFlix app to see the new posters!")
    print()


if __name__ == '__main__':
    main()
