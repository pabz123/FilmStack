# MovieFlix - Port 8765 Conflict Fix

## Problem: Backend Failed to Start - Port Already in Use

### Error Message:
```
Backend failed to start!
Port 8765 is already in use
Unable to connect to backend
```

---

## ✅ SOLUTION APPLIED

### Step 1: Kill All Processes on Port 8765 ✅

**Created:** `kill_port_8765.bat`

This script:
- Finds all processes using port 8765
- Kills them forcefully
- Verifies port is free
- Ready to use anytime!

**Usage:**
```cmd
kill_port_8765.bat
```

### Step 2: Updated Complete Launcher ✅

**Updated:** `start_movieflix_complete.bat`

Now automatically:
1. ✅ Checks if backend is running
2. ✅ **NEW:** Checks if port 8765 is in use
3. ✅ **NEW:** Automatically kills conflicting processes
4. ✅ Starts backend with uvicorn
5. ✅ Waits for backend to be ready
6. ✅ Launches MovieFlix

---

## 🚀 How to Use

### Option 1: Use Complete Launcher (Easiest)
```cmd
start_movieflix_complete.bat
```
- Handles everything automatically
- Kills port conflicts
- Starts backend
- Launches MovieFlix

### Option 2: Manual Port Kill + Start
```cmd
# Step 1: Kill port 8765 processes
kill_port_8765.bat

# Step 2: Start MovieFlix
start_movieflix_complete.bat
```

### Option 3: Desktop Shortcut
```cmd
# Create/update desktop shortcut (one-time)
create_desktop_shortcut.bat

# Then use desktop icon normally
Double-click "MovieFlix" on desktop
```

---

## 🔧 What Causes Port Conflicts?

### Common Causes:
1. **Previous MovieFlix instance still running**
   - Backend didn't close properly
   - Python process stuck

2. **Another application using port 8765**
   - Rare, but possible
   - Could be another web server

3. **Crash/Force close**
   - MovieFlix closed abnormally
   - Backend process orphaned

---

## 📝 Files Created/Updated

### New Files:
- ✅ `kill_port_8765.bat` - Port cleanup utility

### Updated Files:
- ✅ `start_movieflix_complete.bat` - Auto port cleanup
- ✅ `start_movieflix.py` - Fixed uvicorn command
- ✅ `create_desktop_shortcut.bat` - Better shortcut

---

## 🐛 Troubleshooting

### Issue: "Port 8765 still in use after running kill script"

**Solution 1: Run kill script again**
```cmd
kill_port_8765.bat
```

**Solution 2: Kill all Python processes**
```cmd
taskkill /F /IM python.exe
taskkill /F /IM pythonw.exe
```

**Solution 3: Find and kill specific PID**
```cmd
# Find the PID
netstat -ano | findstr ":8765"

# Kill it (replace 12345 with actual PID)
taskkill /F /PID 12345
```

**Solution 4: Restart computer** (nuclear option)

### Issue: "Backend starts but still can't connect"

**Check 1: Is it actually running?**
```cmd
# Check processes
tasklist | findstr python

# Check port
netstat -ano | findstr ":8765"
```

**Check 2: Test backend directly**
Open in browser: http://localhost:8765/docs

If you see FastAPI docs, backend is working!

**Check 3: Firewall blocking?**
- Allow Python in Windows Firewall
- Check antivirus settings

### Issue: "MovieFlix closes immediately after starting"

**Possible causes:**
1. Backend not ready yet - Wait 5-10 seconds
2. VLC not found - Check VLC folder exists
3. Database error - Delete movies.db and restart

**Debug:**
```cmd
# Run with visible console to see errors
venv\Scripts\python.exe start_movieflix.py
```

---

## 📊 How the Complete Launcher Works

### New Process Flow:

```
start_movieflix_complete.bat
        ↓
Step 1: Check if backend running
        ↓ No
Step 2: Check if port 8765 in use
        ↓ Yes
    Kill processes on port 8765
        ↓
    Wait 2 seconds
        ↓
Step 3: Start backend with uvicorn
        ↓
Step 4: Wait for backend (up to 15 sec)
        ↓ Check every 0.5 sec
    Backend ready?
        ↓ Yes
Step 5: Launch MovieFlix
        ↓
Login screen appears
```

---

## ✅ Verification Steps

After running the fix, verify it works:

**1. Port is free:**
```cmd
netstat -ano | findstr ":8765"
```
Should show nothing or "LISTENING" with your new process.

**2. Backend is running:**
```cmd
curl http://localhost:8765/docs
```
Or open in browser.

**3. MovieFlix connects:**
- Start MovieFlix
- Login screen should appear
- Enter credentials: admin / admin123
- Should login successfully ✅

---

## 🎯 Summary

**Problem:** Port 8765 in use → Backend failed to start

**Root Causes:**
1. Old MovieFlix/backend processes still running
2. Improper shutdown left processes

**Solutions:**
1. ✅ Created `kill_port_8765.bat` - Manual port cleanup
2. ✅ Updated `start_movieflix_complete.bat` - Auto port cleanup
3. ✅ Updated desktop shortcut to use complete launcher

**Result:** 
- Port conflicts automatically resolved
- Backend starts reliably
- MovieFlix works every time ✅

---

## 📞 Quick Commands

```cmd
# Kill port 8765 processes
kill_port_8765.bat

# Start MovieFlix (with auto port cleanup)
start_movieflix_complete.bat

# Create/update desktop shortcut
create_desktop_shortcut.bat

# Check if backend running
curl http://localhost:8765/docs

# Manual backend start (for debugging)
venv\Scripts\python.exe -m uvicorn backend.main:app --port 8765

# Check what's using port 8765
netstat -ano | findstr ":8765"
```

---

## 🎬 Ready to Use!

Backend is now running on port 8765.

**Start MovieFlix:**
- Use desktop shortcut, OR
- Run: `start_movieflix_complete.bat`

**Login:** admin / admin123

**Enjoy!** 🍿
