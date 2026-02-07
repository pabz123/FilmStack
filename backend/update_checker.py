"""
Update checker for MovieFlix
Checks GitHub releases for new versions
"""

import requests
from typing import Optional, Dict

# Import version from backend
try:
    from backend.version import __version__ as CURRENT_VERSION
except ImportError:
    CURRENT_VERSION = "1.0.0"

GITHUB_REPO = "pabz123/FilmStack"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

def get_latest_version() -> Optional[Dict]:
    """
    Check GitHub for the latest release.
    
    Returns:
        Dict with version info or None if check fails
    """
    try:
        response = requests.get(GITHUB_API_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'version': data['tag_name'].lstrip('v'),
                'download_url': data['html_url'],
                'release_notes': data['body'],
                'published_at': data['published_at']
            }
    except Exception as e:
        print(f"Failed to check for updates: {e}")
    return None

def is_update_available() -> tuple:
    """
    Check if a newer version is available.
    
    Returns:
        Tuple of (update_available: bool, version_info: dict or None)
    """
    latest = get_latest_version()
    if not latest:
        return False, None
    
    try:
        # Simple version comparison (works for X.Y.Z format)
        current_parts = [int(x) for x in CURRENT_VERSION.split('.')] 
        latest_parts = [int(x) for x in latest['version'].split('.')] 
        
        # Compare major, minor, patch
        for curr, lat in zip(current_parts, latest_parts):
            if lat > curr:
                return True, latest
            elif lat < curr:
                return False, None
        
        return False, None
    except Exception as e:
        print(f"Error comparing versions: {e}")
        return False, None

def get_current_version() -> str:
    """Get the current version of MovieFlix."""
    return CURRENT_VERSION
