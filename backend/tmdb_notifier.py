"""
TMDB New Releases Notification System
"""
import requests
from datetime import datetime, timedelta
import os


class TMDBNotifier:
    """Check for new movies and TV shows"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
    
    def get_new_movies(self, days=7):
        """Get movies released in the last N days"""
        if not self.api_key or self.api_key == "YOUR_API_KEY":
            return []
        
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            params = {
                "api_key": self.api_key,
                "language": "en-US",
                "sort_by": "release_date.desc",
                "release_date.gte": start_date.strftime("%Y-%m-%d"),
                "release_date.lte": end_date.strftime("%Y-%m-%d"),
                "vote_count.gte": 10  # Filter out spam
            }
            
            response = requests.get(
                f"{self.base_url}/discover/movie",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                movies = data.get("results", [])
                
                # Add poster URLs
                for movie in movies:
                    if movie.get("poster_path"):
                        movie["poster_url"] = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
                    else:
                        movie["poster_url"] = None
                
                return movies[:10]  # Return top 10
            
            return []
            
        except Exception as e:
            print(f"Error fetching new movies: {e}")
            return []
    
    def get_trending_today(self):
        """Get today's trending movies and shows"""
        if not self.api_key or self.api_key == "YOUR_API_KEY":
            return []
        
        try:
            params = {
                "api_key": self.api_key,
                "language": "en-US"
            }
            
            response = requests.get(
                f"{self.base_url}/trending/all/day",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                trending = data.get("results", [])
                
                # Add poster URLs
                for item in trending:
                    if item.get("poster_path"):
                        item["poster_url"] = f"https://image.tmdb.org/t/p/w500{item['poster_path']}"
                    else:
                        item["poster_url"] = None
                    
                    # Add type
                    item["media_type"] = item.get("media_type", "unknown")
                    item["display_title"] = item.get("title") or item.get("name", "Unknown")
                
                return trending[:10]
            
            return []
            
        except Exception as e:
            print(f"Error fetching trending: {e}")
            return []
    
    def get_popular_movies(self, page=1):
        """Get popular movies right now"""
        if not self.api_key or self.api_key == "YOUR_API_KEY":
            return []
        
        try:
            params = {
                "api_key": self.api_key,
                "language": "en-US",
                "page": page
            }
            
            response = requests.get(
                f"{self.base_url}/movie/popular",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                movies = data.get("results", [])
                
                for movie in movies:
                    if movie.get("poster_path"):
                        movie["poster_url"] = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
                    else:
                        movie["poster_url"] = None
                
                return movies
            
            return []
            
        except Exception as e:
            print(f"Error fetching popular movies: {e}")
            return []
    
    def get_upcoming_movies(self):
        """Get upcoming movie releases"""
        if not self.api_key or self.api_key == "YOUR_API_KEY":
            return []
        
        try:
            params = {
                "api_key": self.api_key,
                "language": "en-US",
                "page": 1
            }
            
            response = requests.get(
                f"{self.base_url}/movie/upcoming",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                movies = data.get("results", [])
                
                for movie in movies:
                    if movie.get("poster_path"):
                        movie["poster_url"] = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
                    else:
                        movie["poster_url"] = None
                
                return movies[:20]
            
            return []
            
        except Exception as e:
            print(f"Error fetching upcoming movies: {e}")
            return []


# Recommendations for legal download automation
LEGAL_DOWNLOAD_OPTIONS = """
═══════════════════════════════════════════════════════════════
  LEGAL WAYS TO AUTOMATE MOVIE/TV SHOW DOWNLOADS
═══════════════════════════════════════════════════════════════

⚠️  WARNING: Sites like nkiri.com, moviebox, etc. are ILLEGAL
    They distribute copyrighted content without permission.

✅ LEGAL ALTERNATIVES:

1. **Sonarr + Radarr (Recommended)**
   - Sonarr: Automatic TV show downloads
   - Radarr: Automatic movie downloads
   - Monitors your watchlist
   - Integrates with usenet/torrents
   - Automatically downloads new episodes/movies
   - Website: sonarr.tv, radarr.video

2. **Plex + Watchlist**
   - Connect Plex to streaming services you subscribe to
   - Auto-download from legal sources

3. **Torrent Clients (for legal content)**
   - qBittorrent + RSS feeds
   - Monitor release sites automatically
   - Download via RSS automation

4. **Usenet + NZBGet/SABnzbd**
   - Subscribe to usenet service
   - Use indexers to find content
   - Automated downloads

5. **Streaming Service APIs**
   - Netflix, Disney+, Amazon Prime
   - Use their APIs if you have subscription
   - Download for offline viewing (within their apps)


🔧 SETUP EXAMPLE (Sonarr/Radarr):

1. Install Sonarr and Radarr
2. Configure download client (qBittorrent, etc.)
3. Add indexers (torrent sites, usenet)
4. Add your movies/shows to library
5. They auto-download new releases
6. Point MovieFlix to their download folders


📋 NOTIFICATION SYSTEM:

Your MovieFlix app can:
✓ Check TMDB for new releases
✓ Show trending content
✓ Notify about upcoming movies
✓ Display popular content

Then YOU decide where to get them legally:
- Subscription services you pay for
- Legal torrent sites (public domain)
- Purchase/rent from iTunes, Google Play
- Usenet with proper subscription


⚖️  REMEMBER:
Copyright infringement is illegal in most countries.
Support creators by using legal sources.
═══════════════════════════════════════════════════════════════
"""


def print_legal_options():
    """Print legal download automation options"""
    print(LEGAL_DOWNLOAD_OPTIONS)
