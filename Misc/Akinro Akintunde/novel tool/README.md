# Android Forensic Analysis Tool

A comprehensive GUI-based tool that combines concepts from **Andriller**, **MVT (Mobile Verification Toolkit)**, and **MobSF (Mobile Security Framework)** for analyzing Android applications running on emulators.

## Features

### 🔍 Data Extraction (Andriller-like)
- Extract SMS/MMS messages
- Extract contacts and call logs
- Extract media files (images, videos, audio)
- Extract app databases
- Extract system and app logs
- Organized output with extraction reports

### 📊 App Monitoring (MVT-like)
- Real-time network activity monitoring
- File system access tracking
- Process activity monitoring
- System event logging
- App behavior analysis

### 🔐 Security Analysis (MobSF-like)
- Permissions analysis (granted, requested, dangerous)
- Network security analysis
- Vulnerability scanning
- Security configuration checks
- Certificate information

## Prerequisites

1. **Python 3.7+** installed on your system
2. **Android Debug Bridge (ADB)** installed and in system PATH
3. **Android Emulator** running (or physical Android device with USB debugging enabled)

### Installing ADB

**Windows:**
1. Download Android SDK Platform Tools from [Android Developer Site](https://developer.android.com/studio/releases/platform-tools)
2. Extract to a folder (e.g., `C:\Android\platform-tools`)
3. Add `platform-tools` directory to your system PATH
4. Verify: Open Command Prompt and run `adb version`

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt-get install android-tools-adb

# macOS (with Homebrew)
brew install android-platform-tools
```

## Installation

1. Navigate to the tool directory:
   ```bash
   cd "Misc/Akinro Akintunde/novel tool"
   ```

2. (Optional) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies (if any):
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Starting the Tool

1. **Start your Android Emulator** (or connect a physical device)

2. **Verify ADB connection:**
   ```bash
   adb devices
   ```
   You should see your emulator listed (e.g., `emulator-5554`)

3. **Run the tool:**
   ```bash
   python main.py
   ```

### Using the GUI

#### Connection Tab
- **Refresh Connection**: Checks for connected devices/emulators
- **List All Devices**: Shows all connected devices
- **Get Device Info**: Displays detailed device information

#### Data Extraction Tab
1. Click **"Get Installed Apps"** to see all installed packages
2. Select an app from the list (or enter package name manually)
3. Check the data types you want to extract
4. Click **"Extract Data"** to start extraction
5. Results are saved in the `output/[package_name]/[timestamp]/` directory

#### Monitoring Tab
1. Enter the package name of the app to monitor
2. Click **"Start Monitoring"** to begin real-time monitoring
3. Monitor network activity, file system changes, and process activity
4. Click **"Stop Monitoring"** when done

#### Analysis Tab
1. Enter the package name to analyze
2. Select analysis options:
   - Permissions Analysis
   - Network Analysis
   - Security Analysis
   - Vulnerability Scan
3. Click **"Start Analysis"** to begin
4. View results in the analysis output area

#### Logs Tab
- View all operations and events in real-time
- Useful for debugging and tracking tool activity

## Working with Android Emulator

### Starting an Emulator

1. **Using Android Studio:**
   - Open Android Studio
   - Go to Tools → Device Manager
   - Create/Start an emulator

2. **Using Command Line:**
   ```bash
   emulator -avd <AVD_NAME>
   ```

3. **Verify Connection:**
   ```bash
   adb devices
   ```

### Emulator-Specific Features

- ✅ **Automatic Detection**: Tool automatically detects emulators
- ✅ **Root Access**: Works with both rooted and non-rooted devices
- ✅ **Data Extraction**: Pulls data from emulator's file system
- ✅ **Real-time Monitoring**: Monitors emulator activity in real-time
- ✅ **Multiple Emulators**: Can work with multiple connected emulators

## Output Structure

```
output/
├── [package_name]/
│   ├── [timestamp]/
│   │   ├── messages/
│   │   ├── contacts/
│   │   ├── call_logs/
│   │   ├── media/
│   │   ├── databases/
│   │   ├── logs/
│   │   └── extraction_report.json
```

## Troubleshooting

### "No device connected"
- Ensure emulator is running: `adb devices`
- Check if ADB is in PATH: `adb version`
- Try restarting ADB server: `adb kill-server && adb start-server`

### "Permission denied" errors
- Some data requires root access
- For emulators, you may need to enable root: `adb root`
- Physical devices need USB debugging enabled

### Connection issues
- Restart ADB: `adb kill-server && adb start-server`
- Check firewall settings
- Ensure emulator is not in sleep mode

## Security & Privacy

⚠️ **Important Notes:**
- This tool is for **educational and authorized testing purposes only**
- Only use on devices/emulators you own or have explicit permission to analyze
- Extracted data may contain sensitive information - handle with care
- Always comply with local laws and regulations regarding digital forensics

## Project Structure

```
novel tool/
├── main.py                 # Main GUI application
├── modules/
│   ├── __init__.py
│   ├── adb_connector.py   # ADB communication module
│   ├── data_extractor.py  # Data extraction (Andriller-like)
│   ├── app_monitor.py     # App monitoring (MVT-like)
│   └── analyzer.py        # Security analysis (MobSF-like)
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── output/               # Extracted data (created at runtime)
```

## Contributing

This tool was created as part of the F25_4440_S003_G12 project for Android forensic analysis.

## License

This tool is for educational purposes as part of the course project.

## Acknowledgments

This tool combines concepts from:
- **Andriller**: Android forensic toolkit for data extraction
- **MVT (Mobile Verification Toolkit)**: Tool for detecting compromise on Android devices
- **MobSF (Mobile Security Framework)**: Automated security testing framework

---

**Created by:** Akinro Akintunde  
**Project:** F25_4440_S003_G12 - Android Forensic Analysis

