# MovieFlix Enhancement Plan

## Issues to Fix:

### 1. Series Cards Don't Show Play Button ❌
**Problem:** Series cards use AdvancedMovieCard which checks for 'path' field. Series objects don't have paths, episodes do.

**Solution:** 
- Change series cards to show "▶ Watch" button instead
- Button opens episode selection dialog
- Show season/episode count on card

### 2. Can't Determine Season/Episode Playing ❌
**Problem:** No UI indicator showing which episode is playing

**Solution:**
- Show "S1E1 - Episode Title" in player controls
- Display series title + episode info at top
- Update window title during playback

### 3. Only Scans Library Folder ❌
**Problem:** Scanner only looks in `library/` folder

**Solution:**
- Add full PC scan option in settings
- Scan all drives (C:, D:, etc.) for video files
- Exclude system folders (Windows, Program Files, etc.)
- Show progress dialog during scan
- Background scanning with threading

### 4. New & Popular No Posters ❌
**Problem:** TMDB content doesn't show posters properly

**Solution:**
- Fix TMDB poster URL construction
- Ensure `is_tmdb` flag is set correctly
- Add poster loading for TMDB content

### 5. Missing Cast & Details ❌
**Problem:** Only shows basic info (title, rating, overview)

**Solution:**
- Fetch cast from TMDB
- Show director, actors, release date
- Display genres and runtime
- Add "More Info" dialog with full details

## Implementation Order:

1. Fix series cards (show Watch button) ✅ Quick
2. Add season/episode display in player ✅ Medium
3. Full PC scan feature ⚠️ Complex
4. Cast & details display ✅ Medium
5. New & Popular posters ✅ Quick

## Files to Modify:

- `app/advanced_widgets.py` - Series card UI
- `app/embedded_player.py` - Episode info display
- `backend/scanner.py` - Full PC scanning
- `backend/metadata.py` - Cast fetching
- `app/info_dialog.py` - Extended movie info
- `backend/main.py` - Series endpoint enhancement
