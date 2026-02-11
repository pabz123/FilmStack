# Complete Rebuild Guide

## 🔄 How to Rebuild MovieFlix

### Quick Method (Recommended)

The build script automatically cleans old builds:

```batch
build_lite.bat
```

**What it does:**
1. ✅ Removes old `build` folder
2. ✅ Removes old `dist` folder
3. ✅ Installs dependencies
4. ✅ Builds fresh executable
5. ✅ Creates new ZIP file

---

### Manual Clean (If Needed)

If you want to clean manually first:

```batch
clean_build.bat
```

This removes:
- `build/` folder
- `dist/` folder

Then build:
```batch
build_lite.bat
```

---

### Debug Build (With Console)

To see errors during startup:

```batch
build_debug.bat
```

This creates:
- `dist/MovieFlix_Debug/MovieFlix_Debug.exe`
- Console window shows all errors
- Helps identify problems

---

## 📋 Step-by-Step Rebuild Process

### Step 1: Clean (Automatic)
```batch
# The build script does this automatically:
# - Removes build folder
# - Removes dist folder
```

### Step 2: Build
```batch
# For normal build:
build_lite.bat

# OR for debug build:
build_debug.bat
```

### Step 3: Test
```batch
# Test normal build:
cd dist\MovieFlix
MovieFlix.exe

# Test debug build:
cd dist\MovieFlix_Debug
MovieFlix_Debug.exe
```

### Step 4: Distribute
```batch
# ZIP file is already created:
dist\MovieFlix_Lite_v1.0.zip
```

---

## 🛠️ What Gets Cleaned

### Automatic Cleanup (build_lite.bat does this)
- ✅ `build/` - PyInstaller temporary files
- ✅ `dist/` - Previous build output

### NOT Cleaned (Keep These)
- ❌ `venv/` - Virtual environment
- ❌ `backend/movies.db` - Your database
- ❌ `library/` - Your movies
- ❌ Source code files

---

## 🔍 Troubleshooting

### "Access Denied" when cleaning
**Cause:** Files in use

**Fix:**
1. Close MovieFlix if running
2. Close any file explorer windows in build/dist
3. Run clean_build.bat again

### "Failed to remove folder"
**Cause:** Files locked

**Fix:**
```batch
# Force cleanup with PowerShell:
powershell -Command "Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue"
```

### Old files still there
**Cause:** Manual files added

**Fix:**
```batch
# Delete everything in dist except source:
del /s /q dist\*.*
rmdir /s /q dist
```

---

## 📊 Build Comparison

| Type | Script | Console | Size | Use Case |
|------|--------|---------|------|----------|
| **Normal** | build_lite.bat | ❌ No | ~85MB | Distribution |
| **Debug** | build_debug.bat | ✅ Yes | ~95MB | Troubleshooting |

---

## ✅ Complete Rebuild Checklist

- [ ] Close MovieFlix if running
- [ ] Close file explorers in build/dist folders
- [ ] Run `build_lite.bat` (cleans automatically)
- [ ] Wait 2-3 minutes for build
- [ ] Test in `dist\MovieFlix\MovieFlix.exe`
- [ ] If errors, run `build_debug.bat`
- [ ] ZIP file ready: `dist\MovieFlix_Lite_v1.0.zip`

---

## 💡 Tips

**Always rebuild after code changes:**
```batch
build_lite.bat
```

**If backend fails, use debug:**
```batch
build_debug.bat
```

**Manual clean if needed:**
```batch
clean_build.bat
```

**Check what was built:**
```batch
dir dist\MovieFlix
```

---

## 🚀 Quick Commands

```batch
# Clean only (manual)
clean_build.bat

# Build normal version
build_lite.bat

# Build debug version
build_debug.bat

# Test build
cd dist\MovieFlix
MovieFlix.exe

# Test debug build
cd dist\MovieFlix_Debug  
MovieFlix_Debug.exe
```

---

## ⚡ One-Command Rebuild

The easiest way:

```batch
build_lite.bat
```

That's it! It cleans and builds automatically! 🎉

---

**Remember:** 
- Build scripts clean automatically
- No need to manually delete folders
- If errors occur, use debug build
- Debug build shows all errors in console
