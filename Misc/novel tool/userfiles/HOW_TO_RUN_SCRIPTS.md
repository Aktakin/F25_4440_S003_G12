# How to Run Scripts in Custom Scripts Tab

## Quick Start Guide

### Step 1: Open the Tool and Navigate to Custom Scripts Tab
1. Run the AKT Forensic Tool: `python main.py`
2. Wait for the tool window to open
3. Click on the **"Custom Scripts"** tab (located between "Analysis" and "Logs" tabs)

### Step 2: Connect to Device (Required)
1. Go to the **"Connection"** tab first
2. Click **"Refresh Connection"** to detect your emulator
3. Click **"Enable Root (Emulator)"** to enable root access (recommended for data extraction)
4. Verify device is connected (should show device ID like `emulator-5554`)

### Step 3: Load the Template Script (If Needed)
- The template script is **automatically loaded** when you open the Custom Scripts tab
- If you cleared it or want to reload: Click **"📋 Load Template"** button
- This loads the default script that extracts call logs and messages

### Step 4: Configure Script Parameters

#### Package Name
- In the **"Package Name"** field, enter the app package you want to extract from
- **For system data (call logs, SMS)**: Leave as default or use:
  - `com.android.providers.telephony` (for SMS/MMS)
  - `com.android.providers.contacts` (for call logs)
- **For specific app**: Enter the app's package name (e.g., `org.telegram.messenger`)

#### Output Directory
- In the **"Output Directory"** field, specify where extracted data will be saved
- Default: `output/custom_scripts`
- You can:
  - Type a custom path: `output/my_extraction`
  - Click **"📁 Browse"** to select a folder using file browser

### Step 5: Execute the Script

1. **Review the script** in the code editor (optional - to understand what it does)
2. Click the **"▶️ Execute Script"** button
3. Watch the **"Script Execution Output"** area for real-time progress

### Step 6: View Results

The script will:
- Show progress messages in the output area
- Extract data to the specified output directory
- Display success/error messages
- Generate extraction reports

**Check your output directory** for:
- `call_logs/` folder with extracted call log data
- `messages/` folder with extracted SMS/MMS data
- `extraction_report.json` with complete extraction summary

---

## Running Your Own Custom Script

### Option 1: Modify the Template
1. Load the template script
2. Edit the code in the editor to customize it
3. Click **"▶️ Execute Script"** to run your modified version

### Option 2: Write a New Script
1. Click **"🗑️ Clear"** to clear the editor
2. Write your Python script in the editor
3. Make sure your script uses the available variables:
   - `adb` - ADB connector
   - `extractor` - Data extractor
   - `device` - Device ID
   - `package` - Package name
   - `output_dir` - Output directory
4. Click **"▶️ Execute Script"** to run

### Option 3: Load a Saved Script
1. Click **"📂 Load Script"** button
2. Select your `.py` file
3. The script loads into the editor
4. Configure package name and output directory
5. Click **"▶️ Execute Script"** to run

### Option 4: Save Your Script
1. Write or modify your script
2. Click **"💾 Save Script"** button
3. Choose location and filename (saves as `.py` file)
4. You can load it later using **"📂 Load Script"**

---

## Example: Running the Default Template Script

### Complete Workflow:

```
1. Start emulator
   ↓
2. Run: python main.py
   ↓
3. Connection Tab → Enable Root
   ↓
4. Custom Scripts Tab
   ↓
5. Package Name: com.android.providers.telephony
   ↓
6. Output Directory: output/test_extraction
   ↓
7. Click "▶️ Execute Script"
   ↓
8. Watch output area for progress
   ↓
9. Check output/test_extraction/ for results
```

### Expected Output in Script Execution Output Area:

```
[2025-12-15 14:30:00] Starting script execution...
Package: com.android.providers.telephony
Output Directory: output/test_extraction
--------------------------------------------------------------------------------

[*] Starting extraction for package: com.android.providers.telephony
[*] Output directory: output/test_extraction

[+] Extracting call logs...
    ✓ Call log database extracted: output/test_extraction/call_logs/calllog.db
    ✓ Parsed 15 call log entries
    ✓ Saved parsed data to: output/test_extraction/call_logs/call_logs_parsed.json

[+] Extracting messages (SMS/MMS)...
    ✓ SMS database extracted: output/test_extraction/messages/mmssms.db
    ✓ Parsed 42 SMS messages
    ✓ Parsed 3 MMS messages
    ✓ Saved parsed data to: output/test_extraction/messages/messages_parsed.json

[+] Extraction complete!
    ✓ Report saved to: output/test_extraction/extraction_report.json
    ✓ Total call logs extracted: 1
    ✓ Total message databases extracted: 1

[✓] Script execution completed successfully!
```

---

## Troubleshooting

### Script Won't Execute
- **Check device connection**: Go to Connection tab and verify device is connected
- **Check package name**: Make sure package name is entered
- **Check output directory**: Make sure output directory path is valid

### "No device connected" Error
- Go to Connection tab
- Click "Refresh Connection"
- Enable root access
- Return to Custom Scripts tab and try again

### "Permission denied" Errors in Output
- Enable root access in Connection tab
- Some databases require root to access
- Try enabling root and running script again

### Script Runs But No Data Extracted
- Check if the package name is correct
- Verify the app/data exists on the device
- Check output directory for error messages in extraction_report.json
- Some apps store data in encrypted format (cannot be extracted)

### Script Execution Hangs
- Scripts run in background threads
- Wait for completion (check output area)
- If truly stuck, close and restart the tool

### Want to Stop Script
- Click "🛑 Stop Execution" (note: may not immediately stop)
- Scripts run in threads and may complete before stopping
- For immediate stop, close the tool window

---

## Tips for Success

1. **Always enable root** before running extraction scripts
2. **Test with system packages first** (com.android.providers.telephony) before trying app-specific packages
3. **Check the output directory** after execution to see what was extracted
4. **Review the extraction_report.json** for detailed results and any errors
5. **Save your custom scripts** so you can reuse them later
6. **Use the template as a starting point** - it shows best practices for extraction

---

## Quick Reference

| Action | Button/Field | Purpose |
|--------|-------------|---------|
| Load default script | 📋 Load Template | Loads the call logs/messages extraction template |
| Clear editor | 🗑️ Clear | Clears the script editor |
| Save script | 💾 Save Script | Saves script to .py file |
| Load script | 📂 Load Script | Loads script from .py file |
| Select output folder | 📁 Browse | Opens folder browser |
| Run script | ▶️ Execute Script | Executes the script |
| Stop script | 🛑 Stop Execution | Attempts to stop running script |
| Package name | Text field | App package to extract from |
| Output directory | Text field | Where to save extracted data |

---

**Ready to extract data?** Follow the steps above and click "▶️ Execute Script"!

