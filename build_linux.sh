#!/usr/bin/env bash
# ========================================
# MovieFlix Linux Build Script
# Creates a standalone Linux executable
# ========================================
set -e

echo ""
echo "========================================"
echo "  MovieFlix Linux Build"
echo "  (VLC NOT included – install separately)"
echo "========================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source venv/bin/activate
    echo "[OK] Virtual environment activated"
else
    echo "[ERROR] venv not found! Run: python3 -m venv venv && pip install -r requirements.txt"
    exit 1
fi

# Install/update dependencies
echo ""
echo "Step 1/5: Installing dependencies..."
pip install -r requirements.txt --quiet
pip install pyinstaller --quiet
echo "[OK] Dependencies installed"

# Clean old builds
echo ""
echo "Step 2/5: Cleaning old builds..."
rm -rf build dist
echo "[OK] Ready for fresh build"

# Build with PyInstaller
echo ""
echo "Step 3/5: Building Linux executable (2-3 minutes)..."
pyinstaller MovieFlix_Linux.spec --clean --noconfirm
echo "[OK] Build completed"

# Copy additional files
echo ""
echo "Step 4/5: Copying additional files..."
mkdir -p dist/MovieFlix/library
echo "[OK] Created library folder"

if [ ! -f dist/MovieFlix/.env ] && [ -f .env ]; then
    cp .env dist/MovieFlix/.env
    echo "[OK] Copied .env file"
fi

# Create VLC notice
cat > dist/MovieFlix/VLC_REQUIRED.txt << 'EOF'
VLC Media Player Required
==========================

MovieFlix requires VLC Media Player for video playback.

Install VLC on Ubuntu/Debian:
  sudo apt update && sudo apt install vlc

Or visit: https://www.videolan.org/vlc/

VLC will be detected automatically after installation!
EOF
echo "[OK] Created VLC_REQUIRED.txt"

if [ -f USER_README.txt ]; then
    cp USER_README.txt dist/MovieFlix/README.txt
    echo "[OK] Copied README"
fi

# Mark executable as runnable
chmod +x dist/MovieFlix/MovieFlix 2>/dev/null || true

# Create archive
echo ""
echo "Step 5/5: Creating portable archive..."
cd dist
tar -czf MovieFlix_Linux_v1.0.tar.gz MovieFlix/
echo "[OK] Created MovieFlix_Linux_v1.0.tar.gz"
cd ..

# Summary
echo ""
echo "========================================"
echo "  LINUX BUILD COMPLETE!"
echo "========================================"
echo ""
echo "Location:   dist/MovieFlix/"
echo "Executable: dist/MovieFlix/MovieFlix"
echo "Archive:    dist/MovieFlix_Linux_v1.0.tar.gz"
echo ""
echo "IMPORTANT:"
echo "  Users MUST install VLC: sudo apt install vlc"
echo ""
echo "Next Steps:"
echo "  1. Test: ./dist/MovieFlix/MovieFlix"
echo "  2. Upload dist/MovieFlix_Linux_v1.0.tar.gz to GitHub Releases"
echo ""
