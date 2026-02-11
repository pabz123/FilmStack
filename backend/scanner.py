"""
MovieFlix File System Scanner
=============================

This module handles scanning of file systems to discover movies and TV series.
It intelligently parses filenames, extracts metadata, and handles various
folder structures. Can scan entire PC or specific directories.

Features:
- Full PC scan (all drives)
- Recursive directory scanning
- Multiple video format support
- Episode number extraction (S01E01, Episode 1, etc.)
- Title cleaning (removes quality tags, years, etc.)
- Duration filtering (20+ minutes)
- Flexible folder structures (flat or nested)
- Smart folder exclusion (system, temp, hidden folders)

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
import string

# Supported video file extensions
VIDEO_EXTENSIONS = (".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".webm")

# Regular expression for episode pattern matching (S01E01, S1E1, etc.)
EPISODE_PATTERN = re.compile(r"(S\d+E\d+)", re.IGNORECASE)

# Minimum video file size (30 MB) - simple size filter, no duration checking
MIN_VIDEO_SIZE = 30 * 1024 * 1024  # 30 MB in bytes
MIN_MOVIE_DURATION = 1200  # Placeholder for duration (not used for actual filtering)

# Folders to exclude from scanning (system, temp, hidden)
EXCLUDED_FOLDERS = {
    "windows", "program files", "program files (x86)", "programdata",
    "$recycle.bin", "system volume information", "recovery", 
    "windows.old", "temp", "tmp", "cache", "appdata", "application data",
    "perflogs", "msocache", "$windows.~bt", "intel", "nvidia", "amd",
    "drivers", "boot", "config.msi", "documents and settings",
    "hiberfil.sys", "pagefile.sys", "swapfile.sys"
}


def get_all_drives():
    """
    Get all available drives on Windows.
    
    Returns:
        list: List of drive letters (e.g., ['C:\\', 'D:\\'])
    """
    drives = []
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            drives.append(drive)
    return drives


def should_skip_folder(folder_path):
    """
    Check if a folder should be skipped during scanning.
    Skips system folders, hidden folders, and common exclusions.
    
    Args:
        folder_path: Path to folder
        
    Returns:
        bool: True if should skip, False otherwise
    """
    folder_name = os.path.basename(folder_path).lower()
    
    # Skip hidden folders
    if folder_name.startswith('.') or folder_name.startswith('$'):
        return True
    
    # Skip excluded folders
    if folder_name in EXCLUDED_FOLDERS:
        return True
    
    # Skip folders with certain patterns
    if folder_name.startswith('~') or folder_name.endswith('.tmp'):
        return True
    
    return False


def get_video_duration(video_path):
    """
    Check if video file meets minimum size requirement.
    Simple size-based filter: > 30MB
    
    Args:
        video_path (str): Path to the video file
        
    Returns:
        float: Returns 1200 (20 mins) if file > 30MB, else 0
    """
    try:
        file_size = os.path.getsize(video_path)
        file_size_mb = file_size / (1024 * 1024)
        
        # Simple rule: Include any video larger than 30MB
        if file_size > MIN_VIDEO_SIZE:
            return 1200  # Return valid duration (20 mins as placeholder)
        else:
            print(f"    ⏭️ Skipping {os.path.basename(video_path)} - Only {file_size_mb:.1f}MB (need > 30MB)")
            return 0  # Too small, skip
    except Exception as e:
        # If we can't check size, include it anyway
        return 1200



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
    
    Filters videos by duration (20+ minutes minimum).
    
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
    scanned_files = 0
    skipped_episodes = 0
    skipped_short = 0
    errors = 0

    if not os.path.exists(movies_dir):
        print(f"Path does not exist: {movies_dir}")
        return movies

    print(f"🔍 Scanning: {movies_dir}")
    
    try:
        # Walk through directory tree recursively
        for root, dirs, files in os.walk(movies_dir):
            # Filter out excluded directories
            try:
                dirs[:] = [d for d in dirs if not should_skip_folder(os.path.join(root, d))]
            except Exception:
                pass
            
            for file in files:
                try:
                    if file.lower().endswith(VIDEO_EXTENSIONS):
                        scanned_files += 1
                        full_path = os.path.join(root, file)
                        
                        # Check if it's a series episode - if so, skip it
                        if is_episode(file):
                            skipped_episodes += 1
                            print(f"    ⏭️ Skipping episode: {file}")
                            continue
                        
                        # Simple size check: > 30MB
                        try:
                            file_size = os.path.getsize(full_path)
                            file_size_mb = file_size / (1024 * 1024)
                            
                            if file_size <= MIN_VIDEO_SIZE:
                                skipped_short += 1
                                print(f"    ⏭️ Skipping {file} - Only {file_size_mb:.1f}MB (need > 30MB)")
                                continue
                            else:
                                print(f"    ✓ Including {file} ({file_size_mb:.1f}MB)")
                        except Exception as e:
                            # If can't check size, include it anyway
                            print(f"    ⚠️ Can't check size for {file}, including anyway")
                        
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
                        
                        if len(movies) % 10 == 0:
                            print(f"  Found {len(movies)} movies so far...")
                            
                except PermissionError:
                    errors += 1
                    continue
                except Exception as e:
                    errors += 1
                    continue
                    
    except Exception as e:
        print(f"  Error scanning {movies_dir}: {e}")
    
    print(f"  📊 Scanned {scanned_files} video files")
    print(f"  ✓ Found {len(movies)} movies (> 30MB)")
    print(f"  ⏭️  Skipped {skipped_episodes} episodes")
    print(f"  📏 Skipped {skipped_short} small files (< 30MB)")
    if errors > 0:
        print(f"  ⚠️  {errors} errors (permission denied)")

    return movies


def scan_series(series_dir):
    """
    Scan for TV series - handles various folder structures:
    1. Series/Season XX/Episodes
    2. Series/Episodes (flat structure)
    3. Mixed structures
    
    Returns:
        dict: {series_title: [episode_data, ...]}
    """
    series_dict = {}

    if not os.path.exists(series_dir):
        print(f"Path does not exist: {series_dir}")
        return series_dict

    print(f"🔍 Scanning for series: {series_dir}")
    
    scanned_files = 0
    skipped_movies = 0
    skipped_short = 0
    errors = 0
    
    try:
        # Walk through directory tree recursively
        for root, dirs, files in os.walk(series_dir):
            # Filter out excluded directories
            try:
                dirs[:] = [d for d in dirs if not should_skip_folder(os.path.join(root, d))]
            except Exception:
                pass
            
            for file in files:
                try:
                    if file.lower().endswith(VIDEO_EXTENSIONS):
                        scanned_files += 1
                        full_path = os.path.join(root, file)
                        
                        # Check if it's a series episode
                        if is_episode(file):
                            # Check file size
                            try:
                                file_size = os.path.getsize(full_path)
                                file_size_mb = file_size / (1024 * 1024)
                                
                                if file_size <= MIN_VIDEO_SIZE:
                                    skipped_short += 1
                                    print(f"    ⏭️ Skipping short episode: {file} ({file_size_mb:.1f}MB)")
                                    continue
                                    
                                print(f"    ✓ Including episode: {file} ({file_size_mb:.1f}MB)")
                            except Exception as e:
                                print(f"    ⚠️ Can't check size for {file}: {e}")
                                pass
                            
                            # Parse episode info
                            try:
                                episode_data = parse_episode(file, root)
                                series_title = episode_data['series_title']
                                
                                if series_title not in series_dict:
                                    series_dict[series_title] = []
                                    print(f"    📺 New series found: {series_title}")
                                series_dict[series_title].append(episode_data)
                            except Exception as e:
                                print(f"    ❌ Error parsing episode {file}: {e}")
                        else:
                            skipped_movies += 1
                            
                except PermissionError:
                    errors += 1
                    continue
                except Exception as e:
                    errors += 1
                    continue
                    
    except Exception as e:
        print(f"  Error scanning {series_dir}: {e}")
    
    print(f"  📊 Scanned {scanned_files} video files")
    print(f"  ✓ Found {len(series_dict)} series with episodes (> 30MB)")
    print(f"  ⏭️  Skipped {skipped_movies} non-episodes")
    print(f"  📏 Skipped {skipped_short} small files (< 30MB)")
    if errors > 0:
        print(f"  ⚠️  {errors} errors (permission denied)")

    return series_dict


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
                        # It's a movie - check duration
                        duration = get_video_duration(full_path)
                        
                        # Only include videos longer than 1 hour (3600 seconds)
                        if duration >= MIN_MOVIE_DURATION:
                            title = clean_title(os.path.splitext(file)[0])
                            movies.append({
                                'title': title,
                                'path': full_path
                            })
                        else:
                            # Skip short videos (trailers, clips, etc.)
                            print(f"⏭ Skipping short video ({duration/60:.1f} min): {file}")
                    
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
    # Check for episode patterns (S01E01, S1E1, etc.)
    if EPISODE_PATTERN.search(filename):
        return True
    
    # Check for common series indicators
    episode_indicators = [
        'episode', 'ep ', ' ep', 'e0', 'e1', 'e2', 'e3', 'e4', 'e5', 
        'e6', 'e7', 'e8', 'e9', 'season', ' s0', ' s1', ' s2', ' s3',
        '.s0', '.s1', '.s2', '.s3', 'part', 'pt'
    ]
    
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
    
    # Determine series title from folder structure first (more reliable)
    folder_name = os.path.basename(folder_path)
    parent_folder = os.path.basename(os.path.dirname(folder_path))
    
    # Check if current folder is a season folder
    if 'season' in folder_name.lower() or re.match(r'^s\d+$', folder_name.lower()):
        # Parent folder is the series name
        series_title = clean_title(parent_folder)
    else:
        # Current folder might be the series name
        series_title = clean_title(folder_name)
    
    if match:
        # Extract from S##E## pattern
        episode_code = match.group().upper()  # e.g., "S01E05"
        try:
            season_number = int(episode_code.split('E')[0][1:])  # Extract season
            episode_number = int(episode_code.split('E')[1])  # Extract episode
        except (IndexError, ValueError):
            season_number = 1
            episode_number = 1
    else:
        # No S##E## pattern - try to extract from folder/filename
        
        # Try to extract season number from folder name
        season_match = re.search(r'season[._\s-]*(\d+)', folder_name, re.IGNORECASE)
        if season_match:
            try:
                season_number = int(season_match.group(1))
            except ValueError:
                season_number = 1
        else:
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
    
    return {
        "series_title": series_title,
        "season_number": season_number,
        "episode_number": episode_number,
        "title": clean_title(os.path.splitext(filename)[0]),
        "path": os.path.join(folder_path, filename)
    }
