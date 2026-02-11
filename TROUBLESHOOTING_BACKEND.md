# MovieFlix Backend Connection Issues - Troubleshooting

## Problem: "Unable to connect to backend" at login

This error occurs when the backend server fails to start.

---

## ✅ Solution 1: Rebuild with Fixed Code

The issue has been fixed! Rebuild the application:

```batch
build_lite.bat
```

**What was fixed:**
- Better error logging
- Improved backend startup
- More hidden imports in PyInstaller
- Better error messages
- Changed host from 0.0.0.0 to 127.0.0.1

---

## 🔍 Solution 2: Check the Log File

After running MovieFlix.exe, check:
```
movieflix_startup.log
```

This file is created in the same folder as MovieFlix.exe

**Look for:**
- "Backend thread error" - Shows what went wrong
- "Failed to import backend.main.app" - Missing module
- "port 8765 not responding" - Backend didn't start

---

## 🛡️ Solution 3: Windows Firewall

Windows Firewall might be blocking port 8765.

**Fix:**
1. Open Windows Defender Firewall
2. Click "Allow an app through firewall"
3. Click "Change settings"
4. Find "MovieFlix" or "Python"
5. Check both Private and Public
6. Click OK
7. Restart MovieFlix

---

## 🔄 Solution 4: Antivirus

Some antivirus software blocks PyInstaller executables.

**Fix:**
1. Add MovieFlix.exe to antivirus exclusions
2. Restart MovieFlix

**Common antiviruses:**
- Windows Defender
- Avast
- AVG
- Norton
- McAfee

---

## 🎯 Solution 5: Run as Administrator

Try running as administrator:

1. Right-click MovieFlix.exe
2. Select "Run as administrator"
3. Try again

---

## 💻 Solution 6: Check Port Availability

Another program might be using port 8765.

**Check:**
```batch
netstat -ano | findstr :8765
```

If something is using it:
1. Close that program
2. Or change MovieFlix port in .env file:
   ```
   API_PORT=8766
   ```

---

## 📝 Solution 7: Fresh Build

If all else fails, rebuild from scratch:

```batch
# Clean everything
rmdir /s /q build
rmdir /s /q dist

# Rebuild
build_lite.bat
```

---

## 🐛 Debugging Mode

To see detailed errors:

1. Hold Shift while double-clicking MovieFlix.exe
2. A console window will appear
3. Watch for error messages
4. Take a screenshot
5. Report the issue with the screenshot

---

## 📊 Common Error Messages

### "Backend thread error: No module named 'backend'"
**Cause:** Backend folder not bundled properly
**Fix:** Rebuild with fixed MovieFlix_Lite.spec

### "port 8765 not responding after 60s"
**Cause:** Backend started but crashed immediately
**Fix:** Check movieflix_startup.log for Python errors

### "Failed to import backend.main.app"
**Cause:** Missing dependencies
**Fix:** Rebuild with all hidden imports

---

## ✅ Testing the Fix

After rebuilding:

1. Run MovieFlix.exe
2. Watch console output (if visible)
3. Should see:
   ```
   Starting MovieFlix...
   Starting backend server...
   ✓ Backend started
   Launching GUI...
   ```
4. Login screen appears
5. Login works!

---

## 📧 Still Not Working?

Create a GitHub issue with:
1. movieflix_startup.log contents
2. Windows version
3. Steps you've tried
4. Screenshot of error

---

## 🎯 Prevention

For future builds:

1. Always test on clean machine first
2. Check movieflix_startup.log
3. Test with Windows Firewall enabled
4. Test without admin rights
5. Include all dependencies in spec file

---

**Fixed in this update!** Just rebuild with `build_lite.bat` 🚀
