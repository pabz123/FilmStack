import sys
sys.path.insert(0, 'D:/movie_library')

from backend.scanner import scan_entire_pc

print('🔍 Starting full PC scan...')
print('')

def progress_callback(current_folder, found_count):
    print(f'📁 Scanning: {current_folder}')
    print(f'   Found so far: {found_count} files')

results = scan_entire_pc(progress_callback=progress_callback)

print('')
print('=' * 50)
print('SCAN COMPLETE!')
print('=' * 50)
print(f'Movies found: {len(results["movies"])}')
print(f'Series found: {len(results["series"])}')
print('')

if results['movies']:
    print('Sample movies:')
    for movie in results['movies'][:5]:
        print(f'  • {movie["title"]}')
    if len(results['movies']) > 5:
        print(f'  ... and {len(results["movies"]) - 5} more')
    print('')

if results['series']:
    print('Sample series:')
    shown = 0
    for episodes in results['series'][:3]:
        if episodes:
            print(f'  • {episodes[0]["title"]} ({len(episodes)} episodes)')
            shown += 1
    if len(results['series']) > 3:
        print(f'  ... and {len(results["series"]) - 3} more series')
