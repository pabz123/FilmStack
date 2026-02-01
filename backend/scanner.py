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
