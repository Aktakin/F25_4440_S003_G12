# Quick Start Guide - AKT Forensic Tool for 4440

## Prerequisites

### 1. Python 3.7 or Higher
- Check if Python is installed: Open Command Prompt and type `python --version`
- If not installed, download from: https://www.python.org/downloads/
- **Important:** During installation, check "Add Python to PATH"

### 2. Android Debug Bridge (ADB)
- Download Android SDK Platform Tools: https://developer.android.com/studio/releases/platform-tools
- Extract to a folder (e.g., `C:\Android\platform-tools`)
- Add to Windows PATH:
  - Right-click "This PC" → Properties → Advanced System Settings
  - Click "Environment Variables"
  - Under "System Variables", find "Path" → Edit
  - Click "New" → Add: `C:\Android\platform-tools`
  - Click OK on all dialogs
- Verify: Open Command Prompt and type `adb version`

### 3. Android Emulator
- Install Android Studio: https://developer.android.com/studio
- Create and start an emulator (see below)

---

## Step-by-Step Instructions

### Step 1: Start Android Emulator

**Option A - Using Android Studio:**
1. Open Android Studio
2. Go to **Tools** → **Device Manager**
3. Click **▶ Play** button to start an emulator
4. Wait for emulator to fully boot (home screen appears)

**Option B - Using Command Line:**
```bash
# List available emulators
emulator -list-avds

# Start emulator (replace AVD_NAME with your emulator name)
emulator -avd AVD_NAME
```

### Step 2: Verify Emulator Connection

Open Command Prompt and run:
```bash
adb devices
```

You should see:
```
List of devices attached
emulator-5554    device
```

If you see `device`, you're ready! ✅

### Step 3: Run the Tool

**Method 1 - Using the Batch File (Windows - Easiest):**
1. Navigate to the tool folder:
   ```bash
   cd "Misc\Akinro Akintunde\novel tool"
   ```
2. Double-click `run.bat` OR run:
   ```bash
   run.bat
   ```

**Method 2 - Using Python Command:**
1. Open Command Prompt
2. Navigate to the tool folder:
   ```bash
   cd "C:\Users\aktak\OneDrive\Desktop\recent projects\4440project\Misc\Akinro Akintunde\novel tool"
   ```
3. Run the tool:
   ```bash
   python main.py
   ```

**Method 3 - Using Python 3 (if python doesn't work):**
```bash
python3 main.py
```

### Step 4: Using the Tool

1. **Connection Tab:**
   - Click "Refresh Connection" - should detect your emulator
   - Click "Enable Root (Emulator)" to enable root access (recommended)
   - Click "Get Device Info" to see device details

2. **Data Extraction Tab:**
   - Click "Get Installed Apps" to see all apps
   - Select an app from the list
   - Check what data to extract
   - Click "Extract Data"

3. **Enhanced Monitoring Tab:**
   - Enter package name (e.g., `org.telegram.messenger` for Telegram)
   - Check "🔥 ULTRA Monitoring" for comprehensive monitoring
   - Click "Start Ultra Monitoring"
   - Watch real-time events appear with color coding

4. **Analysis Tab:**
   - Enter package name
   - Select analysis options
   - Click "Start Analysis"

---

## Troubleshooting

### "No device connected"
- Make sure emulator is running
- Run `adb devices` to verify connection
- Try: `adb kill-server && adb start-server`
- Click "Refresh Connection" in the tool

### "Python not found"
- Make sure Python is installed and in PATH
- Try `python3` instead of `python`
- Reinstall Python with "Add to PATH" checked

### "ADB not found"
- Make sure ADB is installed and in PATH
- Verify: `adb version` works in Command Prompt
- Add platform-tools to PATH (see Prerequisites)

### "Permission denied" errors
- Enable root: Click "Enable Root (Emulator)" in Connection tab
- Some data requires root access

### Tool window doesn't open
- Check if Python is installed correctly
- Try running from Command Prompt to see error messages
- Make sure tkinter is available (usually comes with Python)

---

## Quick Test

1. Start emulator
2. Run `adb devices` (should show emulator)
3. Run `python main.py` from tool directory
4. Tool window should open with AKT logo
5. Click "Refresh Connection" - should show your emulator
6. Click "Enable Root" - should enable root access
7. You're ready to use the tool!

---

## Example: Monitoring Telegram

1. Install Telegram on emulator (if not already installed)
2. Open tool → Connection tab → Enable Root
3. Go to Enhanced Monitoring tab
4. Enter: `org.telegram.messenger`
5. Check "🔥 ULTRA Monitoring"
6. Click "Start Ultra Monitoring"
7. Open Telegram in emulator and use it
8. Watch events appear in real-time:
   - Login events (green)
   - OTP codes (orange)
   - File changes (purple)
   - Database updates (pink)
   - Network connections (blue)

---

**Need Help?** Check the Logs tab for detailed information about what's happening.

