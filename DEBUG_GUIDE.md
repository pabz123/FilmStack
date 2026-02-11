# Backend Startup Failure - Quick Debug Guide

## 🚨 Problem: "Backend failed to start" popup

This means the backend server couldn't start when MovieFlix.exe ran.

---

## 🔍 STEP 1: Build Debug Version

Run this to create a version that shows errors:

```batch
build_debug.bat
```

This creates `MovieFlix_Debug.exe` with a **console window** showing all errors.

---

## 🔍 STEP 2: Run Debug Version

```batch
cd dist\MovieFlix_Debug
MovieFlix_Debug.exe
```

**Watch the console window!** It will show:
- What's being imported
- Where it fails
- The exact error message

---

## 📋 STEP 3: Common Errors & Solutions

### Error: "No module named 'backend'"
**Cause:** Backend folder not bundled properly

**Fix:**
```batch
# Check if backend folder exists in dist\MovieFlix_Debug\
dir dist\MovieFlix_Debug\backend
```

If missing, the spec file needs to be fixed.

---

### Error: "No module named 'database'"
**Cause:** Backend imports are relative, doesn't work in frozen app

**Fix:** Need to update backend/main.py imports to be absolute

---

### Error: "Cannot find uvicorn" or "Cannot find fastapi"
**Cause:** Missing hidden imports

**Fix:** Already added to spec file, rebuild should fix it

---

### Error: "DLL load failed" or "sqlite3.dll"
**Cause:** Missing DLL files

**Fix:** Need to bundle sqlite3 DLL explicitly

---

### Error: "Permission denied" on port 8765
**Cause:** Firewall or another program using port

**Fix:**
1. Check firewall
2. Run as administrator
3. Or change port in .env

---

## 🔧 STEP 4: Send Me the Error

After running debug version:

1. Take screenshot of console window
2. Or copy the error text
3. Send it back

I can then provide exact fix!

---

## 🎯 Common Quick Fixes

### Fix 1: Try Running as Administrator
```
Right-click MovieFlix_Debug.exe → Run as administrator
```

### Fix 2: Check Firewall
```
Windows Security → Firewall → Allow an app
Add MovieFlix_Debug.exe
```

### Fix 3: Check the Log File
```
Open: movieflix_startup.log
Look for: "Backend thread error"
```

---

## 📊 What to Look For in Console

**GOOD - Backend Starting:**
```
Starting MovieFlix...
Starting backend server...
Backend thread: Importing uvicorn and FastAPI app
Backend thread: Successfully imported backend.main.app
Backend thread: Starting uvicorn server on port 8765
✓ Backend started in 2.5s
Launching GUI...
```

**BAD - Backend Failed:**
```
Starting MovieFlix...
Starting backend server...
Backend thread: Importing uvicorn and FastAPI app
Backend thread: Failed to import backend.main.app: [ERROR HERE]
⚠ Backend failed to start properly!
```

Copy that ERROR and send it!

---

## 🚀 Quick Test Steps

1. **Build debug version:**
   ```batch
   build_debug.bat
   ```

2. **Run it:**
   ```batch
   cd dist\MovieFlix_Debug
   MovieFlix_Debug.exe
   ```

3. **Watch console for errors**

4. **Send error text/screenshot**

---

## 💡 Likely Issues

Based on similar PyInstaller projects:

1. **Import paths** - Backend using relative imports
2. **Missing DLLs** - SQLite3.dll not bundled
3. **File permissions** - Can't write database file
4. **Firewall** - Port 8765 blocked
5. **Missing modules** - Some dependency not included

---

## ✅ Next Steps

After you send the error:

1. I'll identify exact issue
2. Create targeted fix
3. Update build scripts
4. Rebuild and test

Usually fixable in 5-10 minutes once we see the error! 🎯

---

**Run `build_debug.bat` and send me what you see!**
