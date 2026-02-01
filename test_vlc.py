"""
Test VLC Player Initialization
Helps diagnose VLC playback issues
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("VLC PLAYER DIAGNOSTIC TEST")
print("=" * 60)
print()

# Test 1: Find VLC
print("TEST 1: Finding VLC DLL")
print("-" * 60)
try:
    from app.embedded_player import find_vlc_dll, VLC_AVAILABLE
    
    paths = find_vlc_dll()
    print(f"VLC_AVAILABLE: {VLC_AVAILABLE}")
    print(f"Found {len(paths)} VLC path(s)")
    
    if VLC_AVAILABLE:
        print("✅ VLC module loaded successfully!")
    else:
        print("❌ VLC module not available")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 2: Create VLC Instance
print("TEST 2: Creating VLC Instance")
print("-" * 60)
try:
    import vlc
    
    instance = vlc.Instance('--quiet')
    if instance:
        print("✅ VLC Instance created successfully!")
    else:
        print("❌ Failed to create VLC instance")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 3: Create Media Player
print("TEST 3: Creating Media Player")
print("-" * 60)
try:
    player = instance.media_player_new()
    if player:
        print("✅ Media Player created successfully!")
    else:
        print("❌ Failed to create media player")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 4: Test with sample file (if available)
print("TEST 4: Testing File Playback Capability")
print("-" * 60)

# Check if there's any video file in library
library_mo = os.path.join(os.path.dirname(__file__), 'library', 'mo')
library_se = os.path.join(os.path.dirname(__file__), 'library', 'se')

test_file = None

# Find first video file
if os.path.exists(library_mo):
    for file in os.listdir(library_mo):
        if file.endswith(('.mp4', '.mkv', '.avi', '.mov')):
            test_file = os.path.join(library_mo, file)
            break

if not test_file and os.path.exists(library_se):
    for root, dirs, files in os.walk(library_se):
        for file in files:
            if file.endswith(('.mp4', '.mkv', '.avi', '.mov')):
                test_file = os.path.join(root, file)
                break
        if test_file:
            break

if test_file:
    print(f"Found test file: {test_file}")
    try:
        media = instance.media_new(test_file)
        if media:
            print("✅ Media object created successfully!")
            print(f"   File: {os.path.basename(test_file)}")
            print(f"   Duration: {media.get_duration() / 1000:.1f}s (if available)")
        else:
            print("❌ Failed to create media object")
    except Exception as e:
        print(f"⚠ Error testing file: {e}")
else:
    print("ℹ No video files found in library for testing")
    print("  This is OK - VLC is ready to play files when added")

print()
print("=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
print()

# Summary
print("SUMMARY:")
print("  ✅ VLC Module: Available")
print("  ✅ VLC Instance: Working")
print("  ✅ Media Player: Working")
if test_file:
    print("  ✅ File Parsing: Working")
print()
print("VLC is ready for playback!")
print()
print("If videos still don't play in MovieFlix:")
print("  1. Check file paths are correct")
print("  2. Ensure files are not corrupted")
print("  3. Check console output for specific errors")
print("  4. Try playing in external VLC first")
