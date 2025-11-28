# Custom Scripts Feature - User Guide

## Overview
The Custom Scripts tab allows you to write and execute your own Python extraction scripts directly within the AKT Forensic Tool. This feature provides flexibility to create custom data extraction workflows tailored to your specific forensic investigation needs.

## Accessing the Custom Scripts Tab
1. Open the AKT Forensic Tool
2. Navigate to the **"Custom Scripts"** tab (located between "Analysis" and "Logs" tabs)

## Features

### Code Editor
- Full-featured Python code editor with syntax highlighting
- Monospace font (Consolas) for better code readability
- Scrollable text area for long scripts
- Dark theme for comfortable coding

### Template Script
The tool includes a pre-loaded template script that demonstrates how to:
- Extract call logs from Android devices
- Extract SMS/MMS messages
- Parse SQLite databases
- Save extracted data in JSON format
- Generate extraction reports

### Script Management
- **Load Template**: Load the default template script for call logs and messages extraction
- **Clear**: Clear the editor
- **Save Script**: Save your custom script to a `.py` file
- **Load Script**: Load a previously saved script from file

### Execution
- **Execute Script**: Run your custom script with access to ADB and data extractor
- **Stop Execution**: Stop a running script (if needed)
- **Real-time Output**: View script execution output in real-time

## Available Variables in Scripts

When you write a script, the following variables are automatically available:

- `adb`: ADB connector object
  - `adb.shell_command(device, command)` - Execute shell commands
  - `adb.pull_file(device, remote_path, local_path)` - Pull files from device
  - `adb.push_file(device, local_path, remote_path)` - Push files to device
  - `adb.get_device_info(device)` - Get device information
  - `adb.get_installed_packages(device)` - List installed packages

- `extractor`: Data extractor object
  - `extractor.extract_messages(device, package, output_dir)` - Extract messages
  - `extractor.extract_call_logs(device, package, output_dir)` - Extract call logs
  - `extractor.extract_contacts(device, package, output_dir)` - Extract contacts
  - `extractor.extract_media(device, package, output_dir)` - Extract media files
  - `extractor.extract_databases(device, package, output_dir)` - Extract databases

- `device`: Current connected device ID (e.g., "emulator-5554")
- `package`: Package name entered in the Package Name field
- `output_dir`: Output directory path entered in the Output Directory field

### Standard Libraries Available
- `os`: Operating system interface
- `json`: JSON encoder/decoder
- `datetime`: Date and time utilities
- `sqlite3`: SQLite database interface

## Template Script Overview

The template script (`extract_call_logs_and_messages`) demonstrates:

1. **Call Log Extraction**:
   - Pulls call log database from `/data/data/com.android.providers.contacts/databases/calllog.db`
   - Parses SQLite database to extract call entries
   - Saves parsed data as JSON
   - Generates summary report

2. **Message Extraction**:
   - Pulls SMS/MMS databases from common locations
   - Parses SMS and MMS messages
   - Saves combined message data as JSON
   - Handles multiple database locations

3. **Error Handling**:
   - Comprehensive error handling for file operations
   - Graceful handling of missing databases
   - Detailed error reporting

4. **Output Organization**:
   - Creates organized directory structure
   - Saves raw databases and parsed JSON
   - Generates extraction reports

## Usage Example

### Step 1: Load Template
1. Click **"📋 Load Template"** to load the default template

### Step 2: Configure Parameters
1. Enter package name (e.g., `org.telegram.messenger`)
2. Specify output directory (e.g., `output/custom_scripts`)
3. Or click **"📁 Browse"** to select a directory

### Step 3: Customize Script (Optional)
- Modify the template script to suit your needs
- Add additional extraction logic
- Customize output format

### Step 4: Execute Script
1. Click **"▶️ Execute Script"**
2. Watch real-time output in the "Script Execution Output" area
3. Check the output directory for extracted data

## Customizing the Template

You can modify the template script to:
- Extract data from specific app databases
- Parse custom database structures
- Add additional data types
- Implement custom filtering logic
- Generate custom reports

### Example: Extracting from App-Specific Database

```python
# Extract from app's custom database
app_db_path = f'/data/data/{package}/databases/custom.db'
local_db = os.path.join(output_dir, 'custom.db')
if adb.pull_file(device, app_db_path, local_db):
    # Parse custom database
    conn = sqlite3.connect(local_db)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM custom_table")
    data = cursor.fetchall()
    # Process data...
```

## Output Structure

After execution, the output directory will contain:

```
output/custom_scripts/
├── call_logs/
│   ├── calllog.db              # Raw database
│   ├── call_logs_parsed.json   # Parsed call data
│   └── call_logs_summary.json  # Summary report
├── messages/
│   ├── mmssms.db               # Raw SMS/MMS database
│   └── messages_parsed.json    # Parsed message data
└── extraction_report.json      # Complete extraction report
```

## Best Practices

1. **Always test scripts** on test data before using on real investigations
2. **Handle errors gracefully** - Use try/except blocks
3. **Validate inputs** - Check if files exist before processing
4. **Use root access** - Many extractions require root privileges
5. **Document your scripts** - Add comments explaining your logic
6. **Save your scripts** - Use "Save Script" to keep your custom scripts

## Troubleshooting

### "No device connected" Error
- Ensure device is connected in the Connection tab
- Verify ADB connection is working

### "Permission denied" Errors
- Enable root access in the Connection tab
- Some databases require root to access

### Script Execution Errors
- Check script syntax in the editor
- Review error messages in the output area
- Ensure all required variables are available

### Database Parsing Errors
- Database structure may vary between Android versions
- Check database schema before parsing
- Use SQLite browser tools to inspect database structure

## Security Notes

- Scripts execute with the same privileges as the tool
- Always review scripts before execution
- Be cautious with scripts from untrusted sources
- Scripts have access to ADB and can modify device data

## Advanced Usage

### Accessing Additional Modules
You can import additional Python modules in your scripts:
```python
import csv
import hashlib
import base64
# etc.
```

### Custom Data Processing
```python
# Process extracted data
for call in call_logs:
    # Custom processing logic
    processed_data = process_call(call)
    # Save processed data
```

### Integration with Other Tools
```python
# Export data in custom format
export_to_csv(data, output_file)
export_to_xml(data, output_file)
```

---

**Need Help?** Check the Logs tab for detailed execution information and error messages.

