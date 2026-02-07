"""
Update Checker for MovieFlix
Checks GitHub releases for new versions
"""

import requests
from typing import Optional, Dict
try:
    from packaging import version
except ImportError:
    # Fallback if packaging not available
    class version:
        @staticmethod
        def parse(v):
            return tuple(map(int, v.split('.')))

from backend.version import __version__

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
                'release_notes': data.get('body', 'No release notes available.'),
                'published_at': data.get('published_at', ''),
                'assets': data.get('assets', [])
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
        # Parse versions
        if hasattr(version, 'parse'):
            current = version.parse(__version__)
            latest_ver = version.parse(latest['version'])
        else:
            # Fallback comparison
            current = version.parse(__version__)
            latest_ver = version.parse(latest['version'])
        
        if latest_ver > current:
            return True, latest
    except Exception as e:
        print(f"Error comparing versions: {e}")
    
    return False, None


def get_current_version() -> str:
    """Get the current version of MovieFlix."""
    return __version__
