"""
MovieFlix File System Scanner
=============================

This module handles scanning of file systems to discover movies and TV series.
It intelligently parses filenames, extracts metadata, and handles various
folder structures.

Features:
- Recursive directory scanning
- Multiple video format support
- Episode number extraction (S01E01, Episode 1, etc.)
- Title cleaning (removes quality tags, years, etc.)
- Flexible folder structures (flat or nested)

Supported Video Formats:
    .mp4, .mkv, .avi, .mov, .flv, .wmv, .webm

Episode Naming Patterns:
    - S01E01, S1E1 (standard)
    - Episode 01, Episode 1
    - Numeric fallback (001.mkv, 1.mkv)

Folder Structures Supported:
    Movies:
        - Flat: /movies/MovieName.mkv
        - Nested: /movies/MovieName/MovieName.mkv
        
    Series:
        - Season folders: /Series/Season 01/Episode.mkv
        - Flat: /Series/S01E01.mkv
"""

import os
import re

# Supported video file extensions
VIDEO_EXTENSIONS = (".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".webm")

# Regular expression for episode pattern matching (S01E01, S1E1, etc.)
EPISODE_PATTERN = re.compile(r"(S\d+E\d+)", re.IGNORECASE)


def clean_title(title):
    """
    Clean up a title by removing common patterns and junk.
    
    Args:
        title (str): The raw title string
        
    Returns:
        str: Cleaned title
    """
    # Remove common quality indicators
    title = re.sub(r'\b(1080p|720p|480p|2160p|4K|HD|BluRay|WEB-DL|WEBRip|HDRip)\b', '', title, flags=re.IGNORECASE)
    
    # Remove year in parentheses or brackets
    title = re.sub(r'[\(\[]?\d{4}[\)\]]?', '', title)
    
    # Remove common release group patterns
    title = re.sub(r'[\(\[].*?[\)\]]', '', title)
    
    # Remove file extensions
    title = re.sub(r'\.(mp4|mkv|avi|mov|flv|wmv|webm)$', '', title, flags=re.IGNORECASE)
    
    # Replace dots, underscores, hyphens with spaces
    title = title.replace('.', ' ').replace('_', ' ').replace('-', ' ')
    
    # Remove multiple spaces
    title = re.sub(r'\s+', ' ', title)
    
    # Strip and title case
    return title.strip().title()


def scan_movies(movies_dir):
    """
    Scan directory for movie files and extract metadata.
    
    Handles both flat structures (all files in one folder) and nested
    structures (each movie in its own subfolder).
    
    Title Cleaning:
        - Removes year (1990-2099)
        - Removes quality tags (720p, 1080p, BluRay, etc.)
        - Replaces dots/underscores with spaces
        - Trims extra whitespace
    
    Args:
        movies_dir (str): Path to movies directory
        
    Returns:
        list: List of dicts with 'title' and 'path' keys
        
    Example:
        >>> scan_movies('/path/to/movies')
        [
            {'title': 'Inception', 'path': '/path/to/movies/Inception.2010.1080p.mkv'},
            {'title': 'Interstellar', 'path': '/path/to/movies/Interstellar.mkv'}
        ]
    """
    movies = []

    if not os.path.exists(movies_dir):
        print(f"Movies directory does not exist: {movies_dir}")
        return movies

    # Walk through directory tree recursively
    for root, dirs, files in os.walk(movies_dir):
        for file in files:
            if file.lower().endswith(VIDEO_EXTENSIONS):
                full_path = os.path.join(root, file)
                title = os.path.splitext(file)[0]
                
                # Clean up title (remove year, quality tags, etc.)
                title = re.sub(r'\b(19|20)\d{2}\b', '', title)  # Remove year
                title = re.sub(r'\b(720p|1080p|2160p|4K|BluRay|WEB-DL|HDTV)\b', '', title, flags=re.IGNORECASE)
                title = re.sub(r'[._]', ' ', title)  # Replace dots and underscores
                title = ' '.join(title.split())  # Remove extra spaces
                
                movies.append({
                    "title": title.strip() or file,
                    "path": full_path
                })
                print(f"Found movie: {title} at {full_path}")

    return movies


def scan_series(series_dir):
    """
    Scan for TV series - handles various folder structures:
    1. Series/Season XX/Episodes
    2. Series/Episodes (flat structure)
    3. Mixed structures
    """
    series_data = []

    if not os.path.exists(series_dir):
        print(f"Series directory does not exist: {series_dir}")
        return series_data

    # Walk through all directories
    for series_name in os.listdir(series_dir):
        series_path = os.path.join(series_dir, series_name)
        if not os.path.isdir(series_path):
            continue

        print(f"Scanning series: {series_name}")

        # Check if series has season folders or episodes directly
        has_season_folders = False
        for item in os.listdir(series_path):
            item_path = os.path.join(series_path, item)
            if os.path.isdir(item_path) and ('season' in item.lower() or re.match(r's\d+', item, re.IGNORECASE)):
                has_season_folders = True
                break

        if has_season_folders:
            # Structure: Series/Season XX/Episodes
            for season_folder in os.listdir(series_path):
                season_path = os.path.join(series_path, season_folder)
                if not os.path.isdir(season_path):
                    continue

                # Extract season number
                season_number = extract_season_number(season_folder)
                if season_number is None:
                    continue

                print(f"  Season {season_number}")

                # Scan episodes in season folder
                for file in os.listdir(season_path):
                    if file.lower().endswith(VIDEO_EXTENSIONS):
                        episode_data = extract_episode_info(file, series_name, season_number, season_path)
                        if episode_data:
                            series_data.append(episode_data)
                            print(f"    Found episode: S{season_number:02d}E{episode_data['episode_number']:02d}")
        else:
            # Structure: Series/Episodes (flat) - assume Season 1
            print(f"  Flat structure detected, assuming Season 1")
            for file in os.listdir(series_path):
                if file.lower().endswith(VIDEO_EXTENSIONS):
                    episode_data = extract_episode_info(file, series_name, 1, series_path)
                    if episode_data:
                        series_data.append(episode_data)
                        print(f"    Found episode: S01E{episode_data['episode_number']:02d}")

    return series_data


def extract_season_number(folder_name):
    """Extract season number from folder name"""
    # Try patterns like "Season 1", "Season 01", "S01", etc.
    patterns = [
        r'season\s*(\d+)',
        r's(\d+)',
        r'(\d+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, folder_name, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                continue
    
    return None


def extract_episode_info(filename, series_name, season_number, folder_path):
    """Extract episode information from filename"""
    # Try to find S##E## pattern
    match = EPISODE_PATTERN.search(filename)
    
    if match:
        # Extract episode number from S##E## pattern
        episode_code = match.group().upper()  # e.g., "S01E05"
        try:
            episode_number = int(episode_code.split('E')[1])
        except (IndexError, ValueError):
            episode_number = 1
    else:
        # Try to extract episode number from filename (e.g., "Episode 5.mkv", "05.mkv")
        ep_match = re.search(r'(?:episode|ep|e)?[._\s-]*(\d+)', filename, re.IGNORECASE)
        if ep_match:
            try:
                episode_number = int(ep_match.group(1))
            except ValueError:
                episode_number = 1
        else:
            # Default to 1 if can't extract
            episode_number = 1

    return {
        "series_title": series_name,
        "season_number": season_number,
        "episode_number": episode_number,
        "path": os.path.join(folder_path, filename)
    }


def scan_entire_pc(progress_callback=None):
    """
    Scan entire PC for video files (movies and series).
    
    Scans all available drives and directories, excluding system folders.
    
    Args:
        progress_callback (callable): Optional callback function(current_path, found_count)
        
    Returns:
        dict: {'movies': [], 'series': []} with discovered content
        
    Example:
        >>> results = scan_entire_pc(lambda path, count: print(f"Scanning {path}..."))
        >>> print(f"Found {len(results['movies'])} movies")
    """
    import platform
    import string
    
    # Folders to exclude from scanning
    EXCLUDE_FOLDERS = {
        'Windows', 'Program Files', 'Program Files (x86)', 
        'ProgramData', '$Recycle.Bin', 'System Volume Information',
        'AppData', 'node_modules', '.git', '.vscode', 'venv',
        'Windows.old', 'Recovery', 'PerfLogs', 'Boot'
    }
    
    movies = []
    series_dict = {}  # Group episodes by series
    total_found = 0
    
    # Get all available drives
    if platform.system() == 'Windows':
        drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
    else:
        drives = ['/home', '/media', '/mnt']  # Common media locations on Linux/Mac
    
    print(f"Scanning drives: {drives}")
    
    for drive in drives:
        print(f"📁 Scanning drive: {drive}")
        
        for root, dirs, files in os.walk(drive):
            # Skip excluded folders
            dirs[:] = [d for d in dirs if d not in EXCLUDE_FOLDERS]
            
            # Progress callback
            if progress_callback:
                progress_callback(root, total_found)
            
            for file in files:
                if file.lower().endswith(VIDEO_EXTENSIONS):
                    full_path = os.path.join(root, file)
                    
                    # Determine if it's a series or movie
                    if is_episode(file):
                        # It's a series episode
                        episode_data = parse_episode(file, root)
                        series_title = episode_data['series_title']
                        
                        if series_title not in series_dict:
                            series_dict[series_title] = []
                        series_dict[series_title].append(episode_data)
                    else:
                        # It's a movie
                        title = clean_title(os.path.splitext(file)[0])
                        movies.append({
                            'title': title,
                            'path': full_path
                        })
                    
                    total_found += 1
    
    # Convert series dict to list
    series = list(series_dict.values())
    
    print(f"✓ Scan complete! Found {len(movies)} movies and {len(series)} series")
    
    return {
        'movies': movies,
        'series': series
    }


def is_episode(filename):
    """
    Check if a filename appears to be a TV episode.
    
    Args:
        filename (str): The filename to check
        
    Returns:
        bool: True if appears to be an episode, False otherwise
    """
    # Check for episode patterns
    if EPISODE_PATTERN.search(filename):
        return True
    
    # Check for common series indicators
    episode_indicators = ['episode', 'ep', 'e0', 'e1', 'e2', 'e3', 'e4', 'e5', 
                         'e6', 'e7', 'e8', 'e9', 'season']
    
    filename_lower = filename.lower()
    return any(indicator in filename_lower for indicator in episode_indicators)


def parse_episode(filename, folder_path):
    """
    Parse episode information from a filename.
    Extracts series title, season, and episode number.
    
    Args:
        filename (str): The episode filename
        folder_path (str): The folder containing the episode
        
    Returns:
        dict: Episode information
    """
    # Try to extract season/episode from filename (e.g., "S01E05")
    match = EPISODE_PATTERN.search(filename)
    
    if match:
        # Extract from S##E## pattern
        episode_code = match.group().upper()  # e.g., "S01E05"
        try:
            season_number = int(episode_code.split('E')[0][1:])  # Extract season
            episode_number = int(episode_code.split('E')[1])  # Extract episode
        except (IndexError, ValueError):
            season_number = 1
            episode_number = 1
        
        # Series title is everything before the season/episode code
        series_title = clean_title(filename[:match.start()])
    else:
        # No S##E## pattern - try to extract from folder/filename
        season_number = 1
        
        # Try to extract episode number
        ep_match = re.search(r'(?:episode|ep|e)[._\s-]*(\d+)', filename, re.IGNORECASE)
        if ep_match:
            try:
                episode_number = int(ep_match.group(1))
            except ValueError:
                episode_number = 1
        else:
            episode_number = 1
        
        # Use folder name or filename as series title
        folder_name = os.path.basename(folder_path)
        if 'season' in folder_name.lower() or 's0' in folder_name.lower():
            # Parent folder might be series name
            series_title = clean_title(os.path.basename(os.path.dirname(folder_path)))
        else:
            series_title = clean_title(filename)
    
    return {
        "series_title": series_title,
        "season_number": season_number,
        "episode_number": episode_number,
        "title": clean_title(os.path.splitext(filename)[0]),
        "path": os.path.join(folder_path, filename)
    }
