"""
Background TMDB Metadata Fetcher
Automatically fetches posters and ratings for movies on startup
"""
from PyQt5.QtCore import QThread, pyqtSignal
import requests
import re
import time


class TMDBMetadataFetcher(QThread):
    """Background thread to fetch TMDB metadata for movies"""
    
    # Signals
    progress = pyqtSignal(str)  # Progress message
    movie_updated = pyqtSignal(int, dict)  # movie_id, metadata
    finished = pyqtSignal(int, int)  # updated_count, total_count
    
    def __init__(self, api_url, tmdb_api_key):
        super().__init__()
        self.api_url = api_url
        self.tmdb_api_key = tmdb_api_key
        self.tmdb_base_url = "https://api.themoviedb.org/3"
        
    def clean_title(self, title):
        """Clean movie title for better TMDB matching"""
        # Remove common patterns
        patterns = [
            r'\(NKIRI\.COM\)',
            r'\.DOWNLOADED\.FROM\.NKIRI\.COM',
            r'\(Awafim\.tv\)',
            r'\.WEB-DL',
            r'\.BluRay',
            r'\.HDTV',
            r'\.DVDRip',
            r'\.BRRip',
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
    
    def search_tmdb_movie(self, title, year=None):
        """Search TMDB for a movie"""
        if not self.tmdb_api_key or self.tmdb_api_key == "YOUR_API_KEY":
            return None
            
        try:
            params = {
                "api_key": self.tmdb_api_key,
                "language": "en-US",
                "query": title,
                "include_adult": "false"
            }
            
            if year:
                params["year"] = year
            
            response = requests.get(
                f"{self.tmdb_base_url}/search/movie",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                if results:
                    return results[0]  # Return best match
            
            return None
        except Exception as e:
            print(f"Error searching TMDB: {e}")
            return None
    
    def search_tmdb_tv(self, title, year=None):
        """Search TMDB for a TV show"""
        if not self.tmdb_api_key or self.tmdb_api_key == "YOUR_API_KEY":
            return None
            
        try:
            params = {
                "api_key": self.tmdb_api_key,
                "language": "en-US",
                "query": title,
                "include_adult": "false"
            }
            
            if year:
                params["first_air_date_year"] = year
            
            response = requests.get(
                f"{self.tmdb_base_url}/search/tv",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                if results:
                    return results[0]
            
            return None
        except Exception as e:
            print(f"Error searching TMDB TV: {e}")
            return None
    
    def run(self):
        """Run the background fetching"""
        try:
            print("🔍 Starting background TMDB metadata fetch...")
            self.progress.emit("Fetching movie metadata from TMDB...")
            
            # Get all movies without posters or ratings
            response = requests.get(f"{self.api_url}/movies", timeout=10)
            
            if response.status_code != 200:
                print("Failed to fetch movies from API")
                self.finished.emit(0, 0)
                return
            
            movies = response.json()
            movies_to_update = [m for m in movies if not m.get('poster') or not m.get('rating')]
            
            print(f"Found {len(movies_to_update)} movies needing metadata (out of {len(movies)} total)")
            
            updated_count = 0
            
            for i, movie in enumerate(movies_to_update):
                movie_id = movie.get('id')
                title = movie.get('title', '')
                
                self.progress.emit(f"Searching TMDB: {title} ({i+1}/{len(movies_to_update)})")
                
                # Clean title and search
                clean_title_str, year = self.clean_title(title)
                tmdb_data = self.search_tmdb_movie(clean_title_str, year)
                
                if tmdb_data:
                    # Prepare metadata update
                    metadata = {}
                    
                    if tmdb_data.get('poster_path'):
                        metadata['poster'] = tmdb_data['poster_path']
                    
                    if tmdb_data.get('vote_average'):
                        metadata['rating'] = tmdb_data['vote_average']
                    
                    if tmdb_data.get('overview'):
                        metadata['overview'] = tmdb_data['overview']
                    
                    # Update via API
                    if metadata:
                        try:
                            update_response = requests.patch(
                                f"{self.api_url}/movies/{movie_id}/metadata",
                                json=metadata,
                                timeout=10
                            )
                            
                            if update_response.status_code == 200:
                                print(f"✓ Updated metadata for: {title}")
                                self.movie_updated.emit(movie_id, metadata)
                                updated_count += 1
                        except Exception as e:
                            print(f"Failed to update {title}: {e}")
                
                # Rate limiting - be nice to TMDB API
                time.sleep(0.3)
            
            # Also fetch metadata for series
            try:
                series_response = requests.get(f"{self.api_url}/series", timeout=10)
                if series_response.status_code == 200:
                    series = series_response.json()
                    series_to_update = [s for s in series if not s.get('poster')]
                    
                    print(f"Found {len(series_to_update)} series needing metadata")
                    
                    for i, show in enumerate(series_to_update):
                        series_id = show.get('id')
                        title = show.get('title', '')
                        
                        self.progress.emit(f"Searching TMDB: {title} ({i+1}/{len(series_to_update)})")
                        
                        clean_title_str, year = self.clean_title(title)
                        tmdb_data = self.search_tmdb_tv(clean_title_str, year)
                        
                        if tmdb_data:
                            metadata = {}
                            
                            if tmdb_data.get('poster_path'):
                                metadata['poster'] = tmdb_data['poster_path']
                            
                            if tmdb_data.get('overview'):
                                metadata['overview'] = tmdb_data['overview']
                            
                            if metadata:
                                try:
                                    requests.patch(
                                        f"{self.api_url}/series/{series_id}/metadata",
                                        json=metadata,
                                        timeout=10
                                    )
                                    print(f"✓ Updated metadata for series: {title}")
                                    updated_count += 1
                                except:
                                    pass
                        
                        time.sleep(0.3)
            except Exception as e:
                print(f"Error fetching series metadata: {e}")
            
            self.progress.emit(f"✓ Metadata fetch complete! Updated {updated_count} items")
            self.finished.emit(updated_count, len(movies_to_update))
            print(f"✓ Background metadata fetch complete: {updated_count} items updated")
            
        except Exception as e:
            print(f"Error in background metadata fetch: {e}")
            import traceback
            traceback.print_exc()
            self.finished.emit(0, 0)
