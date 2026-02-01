# MovieFlix - Desktop Shortcut Fix Guide

## Problem: "Unable to Connect to Backend" on Login

### Root Cause
The desktop shortcut (MovieFlix.vbs) was launching `start_movieflix.py`, but the backend wasn't starting properly because:
1. Wrong command: Used `python backend/main.py` instead of `uvicorn module`
2. Silent errors: `pythonw.exe` hides console, so backend errors weren't visible

---

## ✅ Fixes Applied

### 1. Fixed Backend Startup Command
**File:** `start_movieflix.py`

**Changed from:**
```python
subprocess.Popen([venv_python, backend_main], ...)
# Tried to run: pythonw.exe backend/main.py
```

**Changed to:**
```python
subprocess.Popen(
    [venv_python, '-m', 'uvicorn', 'backend.main:app', '--host', '0.0.0.0', '--port', '8765'],
    ...
)
# Runs: pythonw.exe -m uvicorn backend.main:app --port 8765
```

### 2. Created Better Desktop Shortcut
**File:** `create_desktop_shortcut.bat`

Creates a shortcut that points to `start_movieflix_complete.bat` which:
- ✅ Checks if backend is running
- ✅ Starts backend with proper uvicorn command
- ✅ Waits for backend to be ready (with timeout)
- ✅ Shows error messages if backend fails
- ✅ Then launches MovieFlix

### 3. Improved Complete Launcher
**File:** `start_movieflix_complete.bat`

Now includes:
- ✅ 15-second timeout with error message
- ✅ Clear troubleshooting steps
- ✅ Uses `pythonw.exe` for backend (no console window)
- ✅ Checks for MovieFlix.exe or falls back to Python script

---

## 🚀 How to Fix Your Desktop Shortcut

### Quick Fix (Easiest)

**Run this command:**
```cmd
cd D:\movie_library
create_desktop_shortcut.bat
```

This will:
1. Create a new "MovieFlix" shortcut on your desktop
2. This shortcut points to the improved launcher
3. Backend will start properly every time!

### Test It

1. Double-click the new **MovieFlix** shortcut on your desktop
2. Wait for the launcher window to show:
   - "Checking if backend is running..."
   - "Starting backend server..."
   - "Backend is ready!"
   - "Launching MovieFlix..."
3. MovieFlix should appear within 5-10 seconds
4. Login with `admin` / `admin123`
5. Should work! ✅

---

## 🔧 Alternative: Manual Backend Start

If you still have issues, start backend manually first:

**Terminal 1: Backend (keep open)**
```cmd
cd D:\movie_library
venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8765
```

**Terminal 2: MovieFlix**
```cmd
cd D:\movie_library
python start_movieflix.py
```

Or just double-click the desktop shortcut - backend will already be running!

---

## 📝 What Each Launcher Does

### MovieFlix.vbs (Old Desktop Shortcut - AVOID)
```
pythonw.exe start_movieflix.py
```
- ❌ May fail silently
- ❌ No error messages
- ❌ Backend might not start

### start_movieflix.py (Direct Python Script)
```
python start_movieflix.py
```
- ⚠️ Tries to start backend, but may fail silently with pythonw.exe
- ✅ Now uses correct uvicorn command (FIXED!)

### start_movieflix_complete.bat (RECOMMENDED)
```
start_movieflix_complete.bat
```
- ✅ Checks backend first
- ✅ Starts with proper uvicorn command
- ✅ Shows error messages
- ✅ Waits for backend to be ready
- ✅ Most reliable!

### MovieFlix.exe (Standalone - When Built)
```
MovieFlix.exe
```
- ✅ Bundles everything
- ✅ Handles backend internally
- ✅ Most professional

---

## 🐛 Troubleshooting

### Still says "Unable to connect to backend"?

**Check 1: Is backend actually running?**
```cmd
curl http://localhost:8765/docs
```
Or open in browser: http://localhost:8765/docs

**If not working:**

**Check 2: Is port 8765 in use by something else?**
```cmd
netstat -ano | findstr :8765
```

**If you see output:**
```cmd
# Kill the process (replace 1234 with actual PID)
taskkill /F /PID 1234
```

**Check 3: Test backend manually**
```cmd
cd D:\movie_library
venv\Scripts\python.exe -m uvicorn backend.main:app --port 8765
```
Watch for errors in the output.

**Check 4: Check the log file**
```cmd
type D:\movie_library\movieflix_startup.log
```
Look for errors about backend starting.

### Backend starts but still can't connect?

**Possible causes:**
1. **Firewall blocking:** Allow Python in Windows Firewall
2. **Antivirus blocking:** Add exception for movie_library folder
3. **Backend crashed:** Check if Python process is still running:
   ```cmd
   tasklist | findstr python
   ```

### MovieFlix starts but UI doesn't load?

This is a different issue (window creation hang):
- Should be fixed in latest version
- Use `start_movieflix_complete.bat` to launch

---

## ✅ Recommended Setup

**For Daily Use:**

1. **Create desktop shortcut:**
   ```cmd
   create_desktop_shortcut.bat
   ```

2. **Use the shortcut to launch MovieFlix**
   - Double-click "MovieFlix" on desktop
   - Wait 5-10 seconds
   - Login and enjoy!

**For Development:**

1. **Keep backend running in Terminal 1:**
   ```cmd
   venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8765
   ```

2. **Launch MovieFlix from Terminal 2:**
   ```cmd
   python start_movieflix.py
   ```

---

## 📊 Startup Time Expectations

| Method | Time to Login | Notes |
|--------|---------------|-------|
| **start_movieflix_complete.bat** | 5-10 sec | Includes backend startup |
| **MovieFlix.exe** | 5-10 sec | Includes backend startup |
| **Python (backend running)** | 2-3 sec | Backend already started |
| **Manual backend + Python** | 2-3 sec | Fastest for development |

---

## 🎯 Summary

**Problem:** Desktop shortcut gave "Unable to connect to backend"

**Root Cause:** Backend wasn't starting with correct uvicorn command

**Fixes:**
1. ✅ Fixed `start_movieflix.py` to use uvicorn module
2. ✅ Created better desktop shortcut (uses complete launcher)
3. ✅ Improved `start_movieflix_complete.bat` with error handling

**Solution:**
```cmd
# Run once to create new shortcut
create_desktop_shortcut.bat

# Then use desktop shortcut daily
Double-click "MovieFlix" icon
```

**Result:** Backend starts properly, login works! ✅

---

## 📞 Quick Commands

```cmd
# Create new desktop shortcut (do this first!)
cd D:\movie_library
create_desktop_shortcut.bat

# Test the complete launcher
start_movieflix_complete.bat

# Check if backend is running
curl http://localhost:8765/docs

# Start backend manually (for testing)
venv\Scripts\python.exe -m uvicorn backend.main:app --port 8765

# Check startup log
type movieflix_startup.log
```

---

**Your desktop shortcut should now work perfectly!** 🎬
