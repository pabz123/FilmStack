"""
Auto Poster Loader - Background Task
=====================================
Automatically fetches missing posters every 30 seconds.
Stops when all movies/series have posters.
"""

from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import requests
import time
import os
import sys
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Get dynamic API URL
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from backend.config import BACKEND_URL
    API_URL = BACKEND_URL
except ImportError:
    API_URL = 'http://localhost:8765'


class AutoPosterLoader(QThread):
    """Background thread for auto-loading missing posters"""
    
    poster_updated = pyqtSignal(str, str)  # Signal: (movie_id, poster_url)
    status_updated = pyqtSignal(str)  # Status messages
    all_loaded = pyqtSignal()  # All posters loaded
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = False
        self.paused = False
        self.check_interval = 30  # seconds
        
    def run(self):
        """Main loop - runs every 30 seconds"""
        self.running = True
        print("🎨 Auto Poster Loader started")
        
        while self.running:
            if not self.paused:
                try:
                    # Check and fetch missing posters
                    all_complete = self.check_and_fetch_posters()
                    
                    if all_complete:
                        print("✅ All content has posters - auto-loader stopping")
                        self.status_updated.emit("✅ All posters loaded!")
                        self.all_loaded.emit()
                        break
                    
                except Exception as e:
                    print(f"⚠ Auto poster loader error: {e}")
                    self.status_updated.emit(f"⚠ Error: {e}")
            
            # Wait for next interval (checking every second for stop signal)
            for _ in range(self.check_interval):
                if not self.running:
                    break
                time.sleep(1)
        
        print("🛑 Auto Poster Loader stopped")
    
    def check_and_fetch_posters(self):
        """Check for missing posters and fetch them"""
        if not TMDB_API_KEY or TMDB_API_KEY == "YOUR_API_KEY":
            print("⚠ No TMDB API key - skipping poster fetch")
            return True  # Stop trying if no API key
        
        try:
            # Get all movies
            movies_response = requests.get(f'{API_URL}/movies', timeout=10)
            if movies_response.status_code != 200:
                return False
            
            all_movies = movies_response.json()
            
            # Get all series
            series_response = requests.get(f'{API_URL}/series', timeout=10)
            series_list = []
            if series_response.status_code == 200:
                series_list = series_response.json()
            
            # Combine all content
            all_content = []
            
            # Add movies
            for movie in all_movies:
                all_content.append({
                    'id': movie['id'],
                    'title': movie['title'],
                    'poster_url': movie.get('poster_url'),
                    'type': 'movie'
                })
            
            # Add series
            for series in series_list:
                all_content.append({
                    'id': series['id'],
                    'title': series['title'],
                    'poster_url': series.get('poster_url'),
                    'type': 'series'
                })
            
            # Filter items without posters
            missing_posters = [
                item for item in all_content
                if not item.get('poster_url') or not item['poster_url'].startswith('http')
            ]
            
            if not missing_posters:
                print("✅ All content has posters")
                return True  # All done!
            
            print(f"🎨 Found {len(missing_posters)} items without posters - fetching silently...")
            # Don't emit status to avoid UI clutter
            
            # Fetch posters (limit to 5 per cycle to avoid overload)
            batch_size = 5
            for item in missing_posters[:batch_size]:
                if not self.running:
                    break
                
                self.fetch_poster_for_item(item)
                time.sleep(0.5)  # Rate limiting
            
            return False  # More to fetch
            
        except Exception as e:
            print(f"⚠ Error checking posters: {e}")
            return False
    
    def fetch_poster_for_item(self, item):
        """Fetch poster for a single movie or series"""
        try:
            item_id = item['id']
            title = item['title']
            item_type = item['type']
            
            print(f"  → Fetching poster for: {title}")
            
            # Clean title for better matching
            clean_title = self.clean_title(title)
            
            # Search TMDB
            if item_type == 'movie':
                tmdb_result = self.search_tmdb_movie(clean_title)
            else:
                tmdb_result = self.search_tmdb_series(clean_title)
            
            if tmdb_result and tmdb_result.get('poster_path'):
                poster_url = f"{IMAGE_BASE_URL}{tmdb_result['poster_path']}"
                rating = tmdb_result.get('vote_average', 0)
                
                # Update via API
                if item_type == 'movie':
                    update_url = f'{API_URL}/movies/{item_id}/metadata'
                else:
                    update_url = f'{API_URL}/series/{item_id}/metadata'
                
                response = requests.patch(
                    update_url,
                    json={
                        'poster_url': poster_url,
                        'rating': float(rating)
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"    ✅ Poster updated for: {title}")
                    self.poster_updated.emit(str(item_id), poster_url)
                    # Silent mode - no status message
                else:
                    print(f"    ⚠ Update failed: HTTP {response.status_code}")
            else:
                print(f"    ⚠ No poster found for: {title}")
                
        except Exception as e:
            print(f"    ⚠ Error fetching poster: {e}")
    
    def search_tmdb_movie(self, title):
        """Search TMDB for movie"""
        try:
            response = requests.get(
                f"{BASE_URL}/search/movie",
                params={"api_key": TMDB_API_KEY, "query": title},
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                if results:
                    return results[0]
            
            return None
            
        except Exception as e:
            print(f"      ⚠ TMDB movie search error: {e}")
            return None
    
    def search_tmdb_series(self, title):
        """Search TMDB for TV series"""
        try:
            response = requests.get(
                f"{BASE_URL}/search/tv",
                params={"api_key": TMDB_API_KEY, "query": title},
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                if results:
                    return results[0]
            
            return None
            
        except Exception as e:
            print(f"      ⚠ TMDB series search error: {e}")
            return None
    
    def clean_title(self, title):
        """Clean title for better TMDB matching"""
        import re
        
        # Remove common tags
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
            r'\[.*?\]',
            r'\(.*?p\)',
            r'\d{3,4}p',
            r'x264',
            r'x265',
            r'H\.264',
            r'H\.265',
            r'HEVC',
        ]
        
        clean = title
        for pattern in patterns:
            clean = re.sub(pattern, ' ', clean, flags=re.IGNORECASE)
        
        clean = clean.replace('.', ' ').replace('_', ' ')
        clean = ' '.join(clean.split())
        
        return clean.strip()
    
    def stop(self):
        """Stop the loader"""
        print("🛑 Stopping auto poster loader...")
        self.running = False
        self.wait()  # Wait for thread to finish
    
    def pause(self):
        """Pause the loader"""
        self.paused = True
        print("⏸ Auto poster loader paused")
    
    def resume(self):
        """Resume the loader"""
        self.paused = False
        print("▶ Auto poster loader resumed")


class AutoPosterManager:
    """Manager for auto poster loading with UI integration"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.loader = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.start_loader)
        
    def start_auto_loading(self, delay_seconds=5):
        """Start auto-loading after a delay"""
        print(f"🎨 Auto poster loader will start in {delay_seconds} seconds...")
        self.timer.setSingleShot(True)
        self.timer.start(delay_seconds * 1000)
    
    def start_loader(self):
        """Start the background loader"""
        if self.loader and self.loader.isRunning():
            print("⚠ Auto poster loader already running")
            return
        
        print("🎨 Starting auto poster loader...")
        self.loader = AutoPosterLoader(self.parent)
        
        # Connect signals
        self.loader.status_updated.connect(self.on_status_update)
        self.loader.poster_updated.connect(self.on_poster_updated)
        self.loader.all_loaded.connect(self.on_all_loaded)
        
        # Start thread
        self.loader.start()
    
    def stop_loader(self):
        """Stop the loader"""
        if self.loader and self.loader.isRunning():
            self.loader.stop()
            self.loader = None
    
    def on_status_update(self, message):
        """Handle status updates - silent mode (console only)"""
        print(f"📊 {message}")
        # Silent mode - don't show in UI to avoid distracting user
    
    def on_poster_updated(self, item_id, poster_url):
        """Handle poster updated - silent refresh"""
        print(f"✅ Poster updated: {item_id}")
        # Silently refresh UI in background
        if hasattr(self.parent, 'refresh_content'):
            self.parent.refresh_content()
    
    def on_all_loaded(self):
        """Handle all posters loaded - silent completion"""
        print("🎉 All posters loaded!")
        # Silent mode - user doesn't need notification
