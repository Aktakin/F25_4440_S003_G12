# What Happens When You Execute a Script

## Overview
When you click **"▶️ Execute Script"**, the tool runs your Python script with access to the connected Android device. Here's what happens step by step:

---

## Step-by-Step Execution Process

### 1. **Script Validation**
- Tool checks if a device is connected
- Verifies package name is entered
- Verifies output directory is specified
- Checks if script editor has content

### 2. **Script Execution Starts**
- Script runs in a background thread (so GUI doesn't freeze)
- **"▶️ Execute Script"** button becomes disabled
- Output area clears and shows execution start message

### 3. **Real-Time Output Display**
You'll see messages appear in the **"Script Execution Output"** area showing:
- Start timestamp
- Package name being used
- Output directory path
- Progress messages from the script
- Success/error messages
- Completion status

### 4. **What the Default Template Script Does**

The default template script performs these operations:

#### A. **Extract Call Logs**
```
[+] Extracting call logs...
    ✓ Call log database extracted: output/custom_scripts/call_logs/calllog.db
    ✓ Parsed 15 call log entries
    ✓ Saved parsed data to: output/custom_scripts/call_logs/call_logs_parsed.json
```

**What it does:**
- Pulls `/data/data/com.android.providers.contacts/databases/calllog.db` from device
- Parses the SQLite database
- Extracts all call log entries
- Saves as JSON file
- Creates summary report

#### B. **Extract Messages (SMS/MMS)**
```
[+] Extracting messages (SMS/MMS)...
    ✓ SMS database extracted: output/custom_scripts/messages/mmssms.db
    ✓ Parsed 42 SMS messages
    ✓ Parsed 3 MMS messages
    ✓ Saved parsed data to: output/custom_scripts/messages/messages_parsed.json
```

**What it does:**
- Pulls SMS/MMS database from device
- Parses SMS messages
- Parses MMS messages
- Saves combined data as JSON
- Creates summary

#### C. **Generate Report**
```
[+] Extraction complete!
    ✓ Report saved to: output/custom_scripts/extraction_report.json
    ✓ Total call logs extracted: 1
    ✓ Total message databases extracted: 1
```

**What it does:**
- Creates comprehensive extraction report
- Lists all extracted files
- Documents any errors encountered
- Provides extraction summary

### 5. **Files Created**

After execution, check your output directory. You should see:

```
output/custom_scripts/
├── call_logs/
│   ├── calllog.db                    # Raw SQLite database
│   ├── call_logs_parsed.json         # Parsed call data (readable)
│   ├── call_logs_summary.json        # Summary statistics
│
├── messages/
│   ├── mmssms.db                     # Raw SMS/MMS database
│   └── messages_parsed.json          # Parsed messages (readable)
│
└── extraction_report.json            # Complete extraction report
```

---

## Expected Output in Script Execution Area

### Successful Execution:
```
[2025-12-15 14:30:00] Starting script execution...
Package: com.android.providers.telephony
Output Directory: output/custom_scripts
--------------------------------------------------------------------------------

[*] Starting extraction for package: com.android.providers.telephony
[*] Output directory: output/custom_scripts

[+] Extracting call logs...
    ✓ Call log database extracted: output/custom_scripts/call_logs/calllog.db
    ✓ Parsed 15 call log entries
    ✓ Saved parsed data to: output/custom_scripts/call_logs/call_logs_parsed.json

[+] Extracting messages (SMS/MMS)...
    ✓ SMS database extracted: output/custom_scripts/messages/mmssms.db
    ✓ Parsed 42 SMS messages
    ✓ Parsed 3 MMS messages
    ✓ Saved parsed data to: output/custom_scripts/messages/messages_parsed.json

[+] Extraction complete!
    ✓ Report saved to: output/custom_scripts/extraction_report.json
    ✓ Total call logs extracted: 1
    ✓ Total message databases extracted: 1

[✓] Script execution completed successfully!
```

### If Errors Occur:
```
[2025-12-15 14:30:00] Starting script execution...
Package: org.telegram.messenger
Output Directory: output/custom_scripts
--------------------------------------------------------------------------------

[*] Starting extraction for package: org.telegram.messenger
[*] Output directory: output/custom_scripts

[+] Extracting call logs...
    ✗ Failed to pull call log database (may require root access)

[+] Extracting messages (SMS/MMS)...
    ✗ No SMS/MMS databases found (may require root access)

[+] Extraction complete!
    ✓ Report saved to: output/custom_scripts/extraction_report.json
    ✓ Total call logs extracted: 0
    ✓ Total message databases extracted: 0

[✓] Script execution completed successfully!
```

---

## What You Should See

### ✅ **Success Indicators:**
1. **Green text** in output area showing progress
2. **Checkmarks (✓)** for successful operations
3. **File paths** showing where data was saved
4. **Counts** of extracted items (e.g., "Parsed 15 call log entries")
5. **"Script execution completed successfully!"** message
6. **Files created** in your output directory

### ⚠️ **Warning Indicators:**
1. **Orange/yellow text** for warnings
2. **Warning symbols (⚠)** for non-critical issues
3. Messages like "may require root access"

### ❌ **Error Indicators:**
1. **Red text** for errors
2. **X symbols (✗)** for failed operations
3. **Error messages** explaining what went wrong
4. **Exception traces** if script crashes

---

## How to Verify It Worked

### 1. **Check the Output Area**
- Look for success messages with ✓
- Verify no red error messages
- Check that files were created

### 2. **Check the Output Directory**
- Navigate to the output directory you specified
- Verify folders were created (`call_logs/`, `messages/`)
- Check that files exist (`.db` files and `.json` files)

### 3. **Open the JSON Files**
- Open `call_logs_parsed.json` to see call log data
- Open `messages_parsed.json` to see SMS/MMS data
- Open `extraction_report.json` for complete summary

### 4. **Check the Extraction Report**
The `extraction_report.json` file contains:
```json
{
  "package": "com.android.providers.telephony",
  "timestamp": "2025-12-15 14:30:00",
  "call_logs": ["path/to/calllog.db"],
  "messages": ["path/to/mmssms.db"],
  "errors": []
}
```

---

## Common Scenarios

### Scenario 1: Everything Works
- ✅ All databases extracted
- ✅ All data parsed successfully
- ✅ JSON files created
- ✅ Report generated
- **Result:** Success! Check output directory for files.

### Scenario 2: Root Access Required
- ⚠️ "Permission denied" errors
- ⚠️ "Failed to pull" messages
- **Solution:** Enable root access in Connection tab, then retry

### Scenario 3: No Data Found
- ⚠️ "No databases found" messages
- ⚠️ Empty extraction results
- **Possible reasons:**
  - Package name incorrect
  - App not installed
  - Data doesn't exist on device
  - Data is encrypted/inaccessible

### Scenario 4: Script Error
- ❌ Red error messages
- ❌ Exception traceback
- **Solution:** Check script syntax, review error message, fix script

---

## Execution Time

- **Fast extraction** (small databases): 5-10 seconds
- **Medium extraction** (moderate data): 10-30 seconds
- **Large extraction** (lots of data): 30+ seconds

**Note:** The script runs in a background thread, so the GUI remains responsive during execution.

---

## After Execution

1. **Button re-enables**: "▶️ Execute Script" becomes clickable again
2. **Output remains visible**: You can scroll through the output
3. **Files are saved**: Check your output directory
4. **Ready for next run**: You can modify script and run again

---

## Tips

- **Watch the output area** for real-time progress
- **Check the output directory** after execution completes
- **Review the extraction report** for detailed results
- **Enable root access** before running for best results
- **Use system packages** (like `com.android.providers.telephony`) for testing

---

**In Summary:** When you execute the script, it extracts data from your Android device, parses it, saves it as readable JSON files, and shows you progress in real-time. Check the output directory to see your extracted data!

