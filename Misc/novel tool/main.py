#!/usr/bin/env python3
"""
Android Forensic Analysis Tool - AKTIS
Forensic Tool for 4440
Combines concepts from Andriller, MVT, and MobSF
Works with Android Emulator for app data extraction and monitoring
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, font
import threading
import os
import json
import time
import re
import zipfile
import shutil
from datetime import datetime

from modules.adb_connector import ADBConnector
from modules.data_extractor import DataExtractor
from modules.app_monitor import AppMonitor
from modules.enhanced_monitor import EnhancedMonitor
from modules.ultra_monitor import UltraMonitor
from modules.analyzer import Analyzer


class ForensicToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AKTIS Forensic Tool for 4440")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e1e')
        
        # Initialize modules
        self.adb = ADBConnector()
        self.extractor = DataExtractor()
        self.extractor.set_adb(self.adb)
        self.monitor = AppMonitor()
        self.monitor.set_adb(self.adb)
        self.enhanced_monitor = EnhancedMonitor()
        self.enhanced_monitor.set_adb(self.adb)
        self.ultra_monitor = UltraMonitor()
        self.ultra_monitor.set_adb(self.adb)
        self.analyzer = Analyzer()
        self.analyzer.set_adb(self.adb)
        
        # Variables
        self.connected_device = None
        self.monitoring_active = False
        self.enhanced_monitoring_active = False
        self.output_dir = "output"
        self.monitor_events_queue = []
        self.monitor_events_list = []  # Store all events for export
        self.current_monitoring_package = None
        self.export_output_dir = None  # User-selected export directory
        
        self.create_header()
        self.create_widgets()
        self.check_emulator_connection()
        
    def create_header(self):
        """Create header with AKTIS logo and tagline"""
        header_frame = tk.Frame(self.root, bg='#2d2d2d', height=100)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # AKTIS Logo (Text-based)
        logo_frame = tk.Frame(header_frame, bg='#2d2d2d')
        logo_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Large AKTIS text
        logo_font = font.Font(family='Arial', size=36, weight='bold')
        logo_label = tk.Label(logo_frame, text="AKTIS", fg='#4a9eff', bg='#2d2d2d', font=logo_font)
        logo_label.pack()
        
        # Tagline
        tagline_font = font.Font(family='Arial', size=12, weight='normal')
        tagline_label = tk.Label(logo_frame, text="Forensic Tool for 4440", fg='#ffffff', bg='#2d2d2d', font=tagline_font)
        tagline_label.pack()
        
        # Right side info
        info_frame = tk.Frame(header_frame, bg='#2d2d2d')
        info_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        version_label = tk.Label(info_frame, text="v2.0 Enhanced", fg='#888888', bg='#2d2d2d', font=('Arial', 10))
        version_label.pack(anchor=tk.E)
        
        status_label = tk.Label(info_frame, text="Android Forensic Analysis", fg='#4a9eff', bg='#2d2d2d', font=('Arial', 9))
        status_label.pack(anchor=tk.E)
        
    def create_widgets(self):
        # Create notebook for tabs with custom style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#1e1e1e', borderwidth=0)
        style.configure('TNotebook.Tab', background='#2d2d2d', foreground='#ffffff', padding=[20, 10])
        style.map('TNotebook.Tab', background=[('selected', '#4a9eff')])
        
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Connection Tab
        self.create_connection_tab(notebook)
        
        # Data Extraction Tab
        self.create_extraction_tab(notebook)
        
        # Monitoring Tab (Enhanced)
        self.create_monitoring_tab(notebook)
        
        # Analysis Tab
        self.create_analysis_tab(notebook)
        
        # Custom Scripts Tab
        self.create_custom_scripts_tab(notebook)
        
        # Log Tab
        self.create_log_tab(notebook)
        
    def create_connection_tab(self, notebook):
        conn_frame = ttk.Frame(notebook)
        notebook.add(conn_frame, text="Connection")
        
        # Root Status Section
        root_frame = ttk.LabelFrame(conn_frame, text="Root Privileges", padding=10)
        root_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.root_status_label = tk.Label(root_frame, text="Root Status: Checking...", font=('Arial', 11, 'bold'))
        self.root_status_label.pack(side=tk.LEFT, padx=10)
        
        self.enable_root_btn = ttk.Button(root_frame, text="Enable Root (Emulator)", command=self.enable_root_access)
        self.enable_root_btn.pack(side=tk.LEFT, padx=5)
        
        self.disable_root_btn = ttk.Button(root_frame, text="Disable Root", command=self.disable_root_access, state=tk.DISABLED)
        self.disable_root_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(root_frame, text="🔄 Refresh Root Status", command=self.refresh_root_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(root_frame, text="🔍 Diagnose Root Issue", command=self.diagnose_root).pack(side=tk.LEFT, padx=5)
        
        # Device Info Section
        info_frame = ttk.LabelFrame(conn_frame, text="Device Information", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.device_info_text = scrolledtext.ScrolledText(info_frame, height=15, width=60)
        self.device_info_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        btn_frame = ttk.Frame(conn_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Refresh Connection", command=self.check_emulator_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="List All Devices", command=self.list_all_devices).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Get Device Info", command=self.get_device_info).pack(side=tk.LEFT, padx=5)
        
    def create_extraction_tab(self, notebook):
        extract_frame = ttk.Frame(notebook)
        notebook.add(extract_frame, text="Data Extraction")
        
        # App Selection
        app_frame = ttk.LabelFrame(extract_frame, text="Select Application", padding=10)
        app_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(app_frame, text="Package Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.package_entry = ttk.Entry(app_frame, width=40)
        self.package_entry.grid(row=0, column=1, padx=5, pady=5)
        self.package_entry.bind('<KeyRelease>', self.on_package_entry_change)
        ttk.Button(app_frame, text="Get Installed Apps", command=self.list_installed_apps).grid(row=0, column=2, padx=5)
        
        # Apps List
        list_frame = ttk.Frame(extract_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ttk.Label(list_frame, text="Installed Applications:").pack(anchor=tk.W)
        self.apps_listbox = tk.Listbox(list_frame, height=10)
        self.apps_listbox.pack(fill=tk.BOTH, expand=True)
        self.apps_listbox.bind('<<ListboxSelect>>', self.on_app_select)
        
        # Output Directory Selection
        output_frame = ttk.LabelFrame(extract_frame, text="Output Location", padding=10)
        output_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(output_frame, text="Save extracted data to:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.extraction_output_entry = ttk.Entry(output_frame, width=50)
        self.extraction_output_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.extraction_output_entry.insert(0, self.output_dir)
        ttk.Button(output_frame, text="📁 Browse", command=self.select_extraction_output_dir).grid(row=0, column=2, padx=5, pady=5)
        
        # Configure column to expand
        output_frame.columnconfigure(1, weight=1)
        
        # Selected package info label
        self.selected_package_label = ttk.Label(output_frame, text="Selected package: None", foreground="gray")
        self.selected_package_label.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)
        
        # Info label about what will be extracted
        info_frame = ttk.Frame(extract_frame)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        info_text = "📋 All available data from the selected package will be extracted:\n    • App databases  • Shared preferences  • Cache files  • Internal storage  • Logs"
        info_label = ttk.Label(info_frame, text=info_text, foreground="#4a9eff")
        info_label.pack(anchor=tk.W, padx=5)
        
        # Extract Button
        ttk.Button(extract_frame, text="📦 Extract All Data for Selected Package", command=self.start_extraction).pack(pady=10)
        
        # Separator
        ttk.Separator(extract_frame, orient='horizontal').pack(fill=tk.X, padx=10, pady=10)
        
        # SDCard / External Storage Extraction
        sdcard_frame = ttk.LabelFrame(extract_frame, text="📷 Extract Photos, Videos & Files from SDCard", padding=10)
        sdcard_frame.pack(fill=tk.X, padx=10, pady=5)
        
        sdcard_info = "Extract files from external storage (no root required):"
        ttk.Label(sdcard_frame, text=sdcard_info).pack(anchor=tk.W)
        
        # Output folder for SDCard extraction
        sdcard_output_frame = ttk.Frame(sdcard_frame)
        sdcard_output_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(sdcard_output_frame, text="Save to:").pack(side=tk.LEFT, padx=(0, 5))
        self.sdcard_output_entry = ttk.Entry(sdcard_output_frame, width=50)
        self.sdcard_output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.sdcard_output_entry.insert(0, self.output_dir)
        ttk.Button(sdcard_output_frame, text="📁 Browse", command=self.select_sdcard_output_dir).pack(side=tk.LEFT, padx=5)
        
        # Checkboxes for what to extract
        self.extract_dcim = tk.BooleanVar(value=True)
        self.extract_pictures = tk.BooleanVar(value=True)
        self.extract_movies = tk.BooleanVar(value=True)
        self.extract_downloads = tk.BooleanVar(value=True)
        self.extract_documents = tk.BooleanVar(value=False)
        
        checks_frame = ttk.Frame(sdcard_frame)
        checks_frame.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(checks_frame, text="📷 DCIM (Camera)", variable=self.extract_dcim).grid(row=0, column=0, padx=10, sticky=tk.W)
        ttk.Checkbutton(checks_frame, text="🖼️ Pictures", variable=self.extract_pictures).grid(row=0, column=1, padx=10, sticky=tk.W)
        ttk.Checkbutton(checks_frame, text="🎬 Movies", variable=self.extract_movies).grid(row=0, column=2, padx=10, sticky=tk.W)
        ttk.Checkbutton(checks_frame, text="📥 Downloads", variable=self.extract_downloads).grid(row=1, column=0, padx=10, sticky=tk.W)
        ttk.Checkbutton(checks_frame, text="📄 Documents", variable=self.extract_documents).grid(row=1, column=1, padx=10, sticky=tk.W)
        
        ttk.Button(sdcard_frame, text="📷 Extract Media from SDCard", command=self.start_sdcard_extraction).pack(pady=10)
        
    def create_monitoring_tab(self, notebook):
        monitor_frame = ttk.Frame(notebook)
        notebook.add(monitor_frame, text="Enhanced Monitoring")
        
        # Package Selection
        pkg_frame = ttk.LabelFrame(monitor_frame, text="Monitor Package", padding=10)
        pkg_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(pkg_frame, text="Package Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.monitor_package_entry = ttk.Entry(pkg_frame, width=40)
        self.monitor_package_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Enhanced monitoring checkbox
        self.use_enhanced = tk.BooleanVar(value=True)
        self.use_ultra = tk.BooleanVar(value=True)
        ttk.Checkbutton(pkg_frame, text="Enhanced Monitoring (Login, OTP, Detailed Events)", variable=self.use_enhanced).grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        ttk.Checkbutton(pkg_frame, text="🔥 ULTRA Monitoring (EVERY Detail: Intents, Broadcasts, Memory, CPU, Content)", variable=self.use_ultra).grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # Monitoring Controls
        control_frame = ttk.Frame(monitor_frame)
        control_frame.pack(pady=10)
        
        self.monitor_start_btn = ttk.Button(control_frame, text="Start Ultra Monitoring", command=self.start_monitoring)
        self.monitor_start_btn.pack(side=tk.LEFT, padx=5)
        
        self.monitor_stop_btn = ttk.Button(control_frame, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED)
        self.monitor_stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Export controls
        export_frame = ttk.Frame(monitor_frame)
        export_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(export_frame, text="Export Output:").pack(side=tk.LEFT, padx=5)
        self.export_dir_label = ttk.Label(export_frame, text="No folder selected", foreground="gray")
        self.export_dir_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(export_frame, text="📁 Select Export Folder", command=self.select_export_folder).pack(side=tk.LEFT, padx=5)
        self.export_btn = ttk.Button(export_frame, text="💾 Export & Zip Monitoring Data", command=self.export_monitoring_data, state=tk.DISABLED)
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        # Monitoring Output with highlighting
        output_frame = ttk.LabelFrame(monitor_frame, text="Real-time Monitoring Output (Enhanced)", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.monitor_output = scrolledtext.ScrolledText(output_frame, height=15, wrap=tk.WORD)
        self.monitor_output.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for highlighting
        self.monitor_output.tag_config("LOGIN", foreground="#00ff00", background="#1a1a1a")
        self.monitor_output.tag_config("OTP", foreground="#ffaa00", background="#1a1a1a")
        self.monitor_output.tag_config("SECURITY", foreground="#ff0000", background="#1a1a1a")
        self.monitor_output.tag_config("NETWORK", foreground="#00aaff", background="#1a1a1a")
        self.monitor_output.tag_config("FILESYSTEM", foreground="#aa00ff", background="#1a1a1a")
        self.monitor_output.tag_config("DATABASE", foreground="#ff00aa", background="#1a1a1a")
        self.monitor_output.tag_config("ACTIVITY", foreground="#00ffaa", background="#1a1a1a")
        self.monitor_output.tag_config("SERVICE", foreground="#ffaa00", background="#1a1a1a")
        self.monitor_output.tag_config("INTENT", foreground="#ffff00", background="#1a1a1a")
        self.monitor_output.tag_config("BROADCAST", foreground="#00ffff", background="#1a1a1a")
        self.monitor_output.tag_config("PROVIDER", foreground="#ff00ff", background="#1a1a1a")
        self.monitor_output.tag_config("MEMORY", foreground="#ff8800", background="#1a1a1a")
        self.monitor_output.tag_config("CPU", foreground="#88ff00", background="#1a1a1a")
        self.monitor_output.tag_config("PREFERENCES", foreground="#00ff88", background="#1a1a1a")
        self.monitor_output.tag_config("API", foreground="#0088ff", background="#1a1a1a")
        
    def create_analysis_tab(self, notebook):
        analysis_frame = ttk.Frame(notebook)
        notebook.add(analysis_frame, text="Analysis")
        
        # Analysis Options
        options_frame = ttk.LabelFrame(analysis_frame, text="Analysis Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.analyze_permissions = tk.BooleanVar(value=True)
        self.analyze_network = tk.BooleanVar(value=True)
        self.analyze_security = tk.BooleanVar(value=True)
        self.analyze_vulnerabilities = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="Permissions Analysis", variable=self.analyze_permissions).grid(row=0, column=0, padx=5, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Network Analysis", variable=self.analyze_network).grid(row=0, column=1, padx=5, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Security Analysis", variable=self.analyze_security).grid(row=1, column=0, padx=5, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Vulnerability Scan", variable=self.analyze_vulnerabilities).grid(row=1, column=1, padx=5, sticky=tk.W)
        
        ttk.Label(options_frame, text="Package:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.analyze_package_entry = ttk.Entry(options_frame, width=40)
        self.analyze_package_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Button(analysis_frame, text="Start Analysis", command=self.start_analysis).pack(pady=10)
        
        # Analysis Results
        results_frame = ttk.LabelFrame(analysis_frame, text="Analysis Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.analysis_results = scrolledtext.ScrolledText(results_frame, height=15)
        self.analysis_results.pack(fill=tk.BOTH, expand=True)
        
    def create_custom_scripts_tab(self, notebook):
        """Create Custom Scripts tab with code editor and template"""
        scripts_frame = ttk.Frame(notebook)
        notebook.add(scripts_frame, text="Custom Scripts")
        
        # Instructions and Info
        info_frame = ttk.LabelFrame(scripts_frame, text="Custom Extraction Scripts", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        info_text = """Write your own Python extraction scripts here. The script has access to:
        - adb: ADB connector object (adb.shell_command(device, cmd), adb.pull_file(device, remote, local))
        - extractor: Data extractor object (extractor.extract_call_logs(), extractor.extract_messages())
        - device: Current connected device ID
        - package: Package name (for system extraction, default is fine)
        - output_dir: Output directory for extracted data
        
        DEFAULT TEMPLATE: Extracts SYSTEM-LEVEL call logs and SMS/MMS messages from the emulator
        (not from specific apps - extracts all calls and messages stored on the device)"""
        
        info_label = tk.Label(info_frame, text=info_text, justify=tk.LEFT, wraplength=800)
        info_label.pack(anchor=tk.W, padx=5, pady=5)
        
        # Package name input
        pkg_frame = ttk.Frame(scripts_frame)
        pkg_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(pkg_frame, text="Package Name (for system data, leave default):").pack(side=tk.LEFT, padx=5)
        self.script_package_entry = ttk.Entry(pkg_frame, width=40)
        self.script_package_entry.pack(side=tk.LEFT, padx=5)
        self.script_package_entry.insert(0, "com.android.providers.telephony")
        
        # Output directory
        output_frame = ttk.Frame(scripts_frame)
        output_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(output_frame, text="Output Directory:").pack(side=tk.LEFT, padx=5)
        self.script_output_entry = ttk.Entry(output_frame, width=50)
        self.script_output_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.script_output_entry.insert(0, "output/custom_scripts")
        ttk.Button(output_frame, text="📁 Browse", command=self.select_script_output_dir).pack(side=tk.LEFT, padx=5)
        
        # Code Editor
        editor_frame = ttk.LabelFrame(scripts_frame, text="Python Script Editor", padding=10)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Button frame for editor controls
        editor_btn_frame = ttk.Frame(editor_frame)
        editor_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(editor_btn_frame, text="📋 Load Template", command=self.load_template_script).pack(side=tk.LEFT, padx=5)
        ttk.Button(editor_btn_frame, text="🗑️ Clear", command=self.clear_script_editor).pack(side=tk.LEFT, padx=5)
        ttk.Button(editor_btn_frame, text="💾 Save Script", command=self.save_custom_script).pack(side=tk.LEFT, padx=5)
        ttk.Button(editor_btn_frame, text="📂 Load Script", command=self.load_custom_script).pack(side=tk.LEFT, padx=5)
        
        # Execute Script button - right beside Load Script
        self.execute_script_btn = ttk.Button(editor_btn_frame, text="▶️ Execute Script", command=self.execute_custom_script)
        self.execute_script_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(editor_btn_frame, text="🛑 Stop", command=self.stop_script_execution).pack(side=tk.LEFT, padx=5)
        
        # Script editor (code text area)
        self.script_editor = scrolledtext.ScrolledText(editor_frame, height=20, wrap=tk.NONE, 
                                                       font=('Consolas', 10), bg='#1e1e1e', fg='#d4d4d4',
                                                       insertbackground='#ffffff')
        self.script_editor.pack(fill=tk.BOTH, expand=True)
        
        # Load template by default
        self.load_template_script()
        
        # Script output
        output_label_frame = ttk.LabelFrame(scripts_frame, text="Script Execution Output", padding=10)
        output_label_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.script_output = scrolledtext.ScrolledText(output_label_frame, height=10, wrap=tk.WORD,
                                                       font=('Consolas', 9), bg='#1e1e1e', fg='#00ff00')
        self.script_output.pack(fill=tk.BOTH, expand=True)
        
        # Script execution flag
        self.script_executing = False
        
    def load_template_script(self):
        """Load template script for extracting call logs and messages"""
        template = '''"""
Custom Extraction Script Template
Extracts SYSTEM-LEVEL call logs and SMS/MMS messages from Android emulator
This script extracts data from system databases, not from specific apps.
"""

import os
import sqlite3
import json
from datetime import datetime

def extract_call_logs_and_messages(adb, extractor, device, package, output_dir):
    """
    Extract SYSTEM-LEVEL call logs and SMS/MMS messages from the Android device/emulator
    
    This function extracts:
    - Call logs from system call log database
    - SMS/MMS messages from system message database
    
    Note: This extracts system-level data, not app-specific data.
    
    Args:
        adb: ADB connector object
        extractor: Data extractor object
        device: Device ID
        package: Package name (not used for system extraction, but kept for compatibility)
        output_dir: Output directory for extracted data
    
    Returns:
        dict: Extraction results
    """
    results = {
        'extraction_type': 'system_level',
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'call_logs': [],
        'messages': [],
        'errors': []
    }
    
    # Create output directories
    calls_dir = os.path.join(output_dir, 'call_logs')
    messages_dir = os.path.join(output_dir, 'messages')
    os.makedirs(calls_dir, exist_ok=True)
    os.makedirs(messages_dir, exist_ok=True)
    
    print(f"[*] Starting SYSTEM-LEVEL extraction from Android emulator")
    print(f"[*] Extracting: Call Logs and SMS/MMS Messages")
    print(f"[*] Output directory: {output_dir}")
    print(f"[*] Note: This extracts system data, not app-specific data")
    
    # ============================================
    # EXTRACT SYSTEM CALL LOGS
    # ============================================
    print("\\n[+] Extracting SYSTEM call logs from emulator...")
    print("    Source: /data/data/com.android.providers.contacts/databases/calllog.db")
    
    try:
        # System call log database path (all call logs on the device)
        call_log_path = '/data/data/com.android.providers.contacts/databases/calllog.db'
        
        # Pull the call log database
        local_call_db = os.path.join(calls_dir, 'calllog.db')
        if adb.pull_file(device, call_log_path, local_call_db):
            print(f"    ✓ Call log database extracted: {local_call_db}")
            results['call_logs'].append(local_call_db)
            
            # Parse call log database
            try:
                conn = sqlite3.connect(local_call_db)
                cursor = conn.cursor()
                
                # Get call log entries
                cursor.execute("SELECT * FROM calls")
                calls = cursor.fetchall()
                
                # Get column names
                columns = [description[0] for description in cursor.description]
                
                # Save parsed call logs as JSON
                call_logs_json = []
                for call in calls:
                    call_dict = dict(zip(columns, call))
                    call_logs_json.append(call_dict)
                
                json_path = os.path.join(calls_dir, 'call_logs_parsed.json')
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(call_logs_json, f, indent=2, default=str)
                
                print(f"    ✓ Parsed {len(call_logs_json)} call log entries")
                print(f"    ✓ Saved parsed data to: {json_path}")
                
                # Save summary
                summary = {
                    'total_calls': len(call_logs_json),
                    'extraction_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'database_path': local_call_db
                }
                summary_path = os.path.join(calls_dir, 'call_logs_summary.json')
                with open(summary_path, 'w', encoding='utf-8') as f:
                    json.dump(summary, f, indent=2)
                
                conn.close()
            except Exception as e:
                error_msg = f"Error parsing call log database: {str(e)}"
                print(f"    ✗ {error_msg}")
                results['errors'].append(error_msg)
        else:
            error_msg = "Failed to pull call log database (may require root access)"
            print(f"    ✗ {error_msg}")
            results['errors'].append(error_msg)
    except Exception as e:
        error_msg = f"Error extracting call logs: {str(e)}"
        print(f"    ✗ {error_msg}")
        results['errors'].append(error_msg)
    
    # ============================================
    # EXTRACT SYSTEM MESSAGES (SMS/MMS)
    # ============================================
    print("\\n[+] Extracting SYSTEM SMS/MMS messages from emulator...")
    print("    Source: System message databases")
    
    try:
        # System SMS/MMS database paths (all messages on the device)
        sms_paths = [
            '/data/data/com.android.providers.telephony/databases/mmssms.db',
            '/data/data/com.android.mms/databases/mmssms.db',
        ]
        
        for sms_path in sms_paths:
            try:
                local_sms_db = os.path.join(messages_dir, os.path.basename(sms_path))
                if adb.pull_file(device, sms_path, local_sms_db):
                    print(f"    ✓ SMS database extracted: {local_sms_db}")
                    results['messages'].append(local_sms_db)
                    
                    # Parse SMS database
                    try:
                        conn = sqlite3.connect(local_sms_db)
                        cursor = conn.cursor()
                        
                        # Get SMS messages
                        try:
                            cursor.execute("SELECT * FROM sms")
                            sms_messages = cursor.fetchall()
                            sms_columns = [description[0] for description in cursor.description]
                            
                            # Get MMS messages
                            cursor.execute("SELECT * FROM pdu")
                            mms_messages = cursor.fetchall()
                            mms_columns = [description[0] for description in cursor.description] if mms_messages else []
                            
                            # Save parsed SMS as JSON
                            sms_json = []
                            for sms in sms_messages:
                                sms_dict = dict(zip(sms_columns, sms))
                                sms_json.append(sms_dict)
                            
                            mms_json = []
                            for mms in mms_messages:
                                mms_dict = dict(zip(mms_columns, mms))
                                mms_json.append(mms_dict)
                            
                            # Save combined messages
                            messages_data = {
                                'sms': sms_json,
                                'mms': mms_json,
                                'total_sms': len(sms_json),
                                'total_mms': len(mms_json)
                            }
                            
                            json_path = os.path.join(messages_dir, 'messages_parsed.json')
                            with open(json_path, 'w', encoding='utf-8') as f:
                                json.dump(messages_data, f, indent=2, default=str)
                            
                            print(f"    ✓ Parsed {len(sms_json)} SMS messages")
                            print(f"    ✓ Parsed {len(mms_json)} MMS messages")
                            print(f"    ✓ Saved parsed data to: {json_path}")
                            
                            conn.close()
                            break  # Successfully extracted from this path
                        except sqlite3.OperationalError as e:
                            print(f"    ⚠ Database structure may be different: {str(e)}")
                            conn.close()
                    except Exception as e:
                        error_msg = f"Error parsing SMS database: {str(e)}"
                        print(f"    ✗ {error_msg}")
                        results['errors'].append(error_msg)
            except Exception as e:
                continue  # Try next path
        
        if not results['messages']:
            error_msg = "No SMS/MMS databases found (may require root access)"
            print(f"    ✗ {error_msg}")
            results['errors'].append(error_msg)
    except Exception as e:
        error_msg = f"Error extracting messages: {str(e)}"
        print(f"    ✗ {error_msg}")
        results['errors'].append(error_msg)
    
    # ============================================
    # SAVE EXTRACTION REPORT
    # ============================================
    report_path = os.path.join(output_dir, 'extraction_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\\n[+] SYSTEM-LEVEL extraction complete!")
    print(f"    ✓ Report saved to: {report_path}")
    print(f"    ✓ Total call log databases extracted: {len(results['call_logs'])}")
    print(f"    ✓ Total message databases extracted: {len(results['messages'])}")
    print(f"    ✓ All system call logs and messages have been extracted")
    
    return results

# ============================================
# MAIN EXECUTION
# ============================================
# This function will be called by the tool
# Variables: adb, extractor, device, package, output_dir are provided by the tool
# NOTE: This script extracts SYSTEM-LEVEL data (all calls and messages on device)
#       The package variable is not used for system extraction

try:
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Execute SYSTEM-LEVEL extraction (ignores package parameter for system data)
    results = extract_call_logs_and_messages(adb, extractor, device, package, output_dir)
    
    print("\\n[✓] SYSTEM-LEVEL extraction completed successfully!")
    print("    All call logs and messages from the emulator have been extracted.")
    
except Exception as e:
    print(f"\\n[✗] Script execution error: {str(e)}")
    import traceback
    traceback.print_exc()
'''
        
        self.script_editor.delete(1.0, tk.END)
        self.script_editor.insert(1.0, template)
        
    def clear_script_editor(self):
        """Clear the script editor"""
        self.script_editor.delete(1.0, tk.END)
        
    def save_custom_script(self):
        """Save custom script to file"""
        script_content = self.script_editor.get(1.0, tk.END)
        filename = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
            title="Save Custom Script"
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(script_content)
                messagebox.showinfo("Success", f"Script saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save script: {str(e)}")
    
    def load_custom_script(self):
        """Load custom script from file"""
        filename = filedialog.askopenfilename(
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
            title="Load Custom Script"
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    script_content = f.read()
                self.script_editor.delete(1.0, tk.END)
                self.script_editor.insert(1.0, script_content)
                messagebox.showinfo("Success", f"Script loaded from {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load script: {str(e)}")
    
    def select_script_output_dir(self):
        """Select output directory for script execution"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.script_output_entry.delete(0, tk.END)
            self.script_output_entry.insert(0, directory)
    
    def execute_custom_script(self):
        """Execute the custom script"""
        if self.script_executing:
            messagebox.showwarning("Warning", "Script is already executing. Please wait or stop it first.")
            return
        
        if not self.connected_device:
            messagebox.showerror("Error", "No device connected. Please connect to a device first.")
            return
        
        # Get script content
        script_content = self.script_editor.get(1.0, tk.END)
        if not script_content.strip():
            messagebox.showwarning("Warning", "Script editor is empty. Please write or load a script.")
            return
        
        # Get package and output directory
        package = self.script_package_entry.get().strip()
        output_dir = self.script_output_entry.get().strip()
        
        if not package:
            messagebox.showwarning("Warning", "Please enter a package name.")
            return
        
        if not output_dir:
            messagebox.showwarning("Warning", "Please specify an output directory.")
            return
        
        # Clear output
        self.script_output.delete(1.0, tk.END)
        self.script_output.insert(tk.END, f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting script execution...\n")
        self.script_output.insert(tk.END, f"Package: {package}\n")
        self.script_output.insert(tk.END, f"Output Directory: {output_dir}\n")
        self.script_output.insert(tk.END, "-" * 80 + "\n\n")
        
        # Execute in separate thread to prevent GUI freezing
        self.script_executing = True
        self.execute_script_btn.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self._execute_script_thread, 
                                 args=(script_content, package, output_dir),
                                 daemon=True)
        thread.start()
    
    def _execute_script_thread(self, script_content, package, output_dir):
        """Execute script in separate thread"""
        import sys
        import io
        from contextlib import redirect_stdout, redirect_stderr
        
        try:
            # Create output capture
            output_buffer = io.StringIO()
            error_buffer = io.StringIO()
            
            # Prepare script execution environment
            script_globals = {
                '__name__': '__main__',
                '__builtins__': __builtins__,
                'adb': self.adb,
                'extractor': self.extractor,
                'device': self.connected_device,
                'package': package,
                'output_dir': output_dir,
                'os': os,
                'json': json,
                'datetime': datetime,
                'sqlite3': __import__('sqlite3'),
                'script_package_entry': self.script_package_entry,
                'script_output_entry': self.script_output_entry,
            }
            
            # Redirect stdout and stderr
            with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                # Execute the script
                exec(compile(script_content, '<custom_script>', 'exec'), script_globals)
            
            # Get output
            output = output_buffer.getvalue()
            errors = error_buffer.getvalue()
            
            # Update GUI in main thread
            self.root.after(0, self._update_script_output, output, errors, None)
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            self.root.after(0, self._update_script_output, "", "", error_trace)
        finally:
            self.script_executing = False
            self.root.after(0, lambda: self.execute_script_btn.config(state=tk.NORMAL))
    
    def _update_script_output(self, output, errors, exception_trace):
        """Update script output in GUI (called from main thread)"""
        if output:
            self.script_output.insert(tk.END, output)
        if errors:
            self.script_output.insert(tk.END, f"\n[ERRORS]\n{errors}\n", "error")
        if exception_trace:
            self.script_output.insert(tk.END, f"\n[EXCEPTION]\n{exception_trace}\n", "error")
        
        self.script_output.see(tk.END)
        
        # Configure error tag
        self.script_output.tag_config("error", foreground="#ff0000")
        
        # Check if execution completed and show completion message
        if output:
            output_lower = output.lower()
            if "script execution completed successfully" in output_lower or "extraction completed successfully" in output_lower:
                # Success case
                self._show_completion_message(output, success=True)
            elif "script execution error" in output_lower or exception_trace:
                # Error case
                self._show_completion_message(output, success=False)
    
    def _show_completion_message(self, output, success=True):
        """Show completion message with file locations when script completes"""
        try:
            output_dir = self.script_output_entry.get().strip()
            
            if success:
                # Extract file paths from output
                files_found = []
                lines = output.split('\n')
                
                for line in lines:
                    if '✓' in line or 'Saved' in line or 'extracted:' in line.lower():
                        # Extract file paths
                        if 'extracted:' in line.lower():
                            parts = line.split('extracted:')
                            if len(parts) > 1:
                                file_path = parts[1].strip()
                                if os.path.exists(file_path):
                                    files_found.append(file_path)
                        elif 'saved' in line.lower():
                            parts = line.split('saved')
                            if len(parts) > 1:
                                file_path = parts[1].replace('to:', '').replace('to', '').strip()
                                if os.path.exists(file_path):
                                    files_found.append(file_path)
                
                # Count extracted items
                call_logs_count = sum(1 for line in lines if 'call log' in line.lower() and ('extracted' in line.lower() or 'parsed' in line.lower()))
                messages_count = sum(1 for line in lines if ('sms' in line.lower() or 'mms' in line.lower() or 'message' in line.lower()) and ('extracted' in line.lower() or 'parsed' in line.lower()))
                
                # Build success message
                success_msg = "✅ Script Execution Completed Successfully!\n\n"
                success_msg += f"📁 Output Directory:\n   {os.path.abspath(output_dir)}\n\n"
                
                if files_found:
                    success_msg += "📄 Key Files Created:\n"
                    # Show key files
                    key_files = []
                    for f in files_found:
                        if any(x in f.lower() for x in ['call_logs_parsed.json', 'messages_parsed.json', 'extraction_report.json', 'summary.json']):
                            key_files.append(f)
                    
                    if key_files:
                        for f in key_files[:5]:  # Show max 5 files
                            try:
                                rel_path = os.path.relpath(f, output_dir)
                                success_msg += f"   • {rel_path}\n"
                            except:
                                success_msg += f"   • {os.path.basename(f)}\n"
                    
                    if len(files_found) > len(key_files):
                        success_msg += f"   ... and {len(files_found) - len(key_files)} more file(s)\n"
                
                # Add summary
                if call_logs_count > 0 or messages_count > 0:
                    success_msg += "\n📊 Extraction Summary:\n"
                    if call_logs_count > 0:
                        success_msg += f"   ✓ Call logs extracted and parsed\n"
                    if messages_count > 0:
                        success_msg += f"   ✓ Messages (SMS/MMS) extracted and parsed\n"
                
                success_msg += f"\n💡 All files are saved in:\n   {os.path.abspath(output_dir)}"
                
                # Show messagebox
                messagebox.showinfo("✅ Execution Complete", success_msg)
                
                # Also add to output with highlighting
                self.script_output.insert(tk.END, "\n" + "="*80 + "\n", "success_header")
                self.script_output.insert(tk.END, "✅ EXECUTION COMPLETED SUCCESSFULLY!\n", "success")
                self.script_output.insert(tk.END, f"📁 Output Directory: {os.path.abspath(output_dir)}\n", "success")
                if files_found:
                    self.script_output.insert(tk.END, f"📄 {len(files_found)} file(s) created\n", "success")
                self.script_output.insert(tk.END, "="*80 + "\n", "success_header")
                
                # Configure success tags
                self.script_output.tag_config("success", foreground="#00ff00", font=('Consolas', 9, 'bold'))
                self.script_output.tag_config("success_header", foreground="#00ff00")
            else:
                # Error case
                error_msg = "❌ Script Execution Completed with Errors\n\n"
                error_msg += f"📁 Output Directory: {os.path.abspath(output_dir)}\n\n"
                error_msg += "⚠️ Please check the output area above for error details.\n"
                error_msg += "Common issues:\n"
                error_msg += "   • Root access may be required\n"
                error_msg += "   • Device may not be connected\n"
                error_msg += "   • Package name may be incorrect\n"
                
                messagebox.showwarning("⚠️ Execution Complete (with errors)", error_msg)
                
                # Add error summary to output
                self.script_output.insert(tk.END, "\n" + "="*80 + "\n", "error_header")
                self.script_output.insert(tk.END, "❌ EXECUTION COMPLETED WITH ERRORS\n", "error_bold")
                self.script_output.insert(tk.END, f"📁 Output Directory: {os.path.abspath(output_dir)}\n", "error")
                self.script_output.insert(tk.END, "⚠️ Review errors above for details\n", "error")
                self.script_output.insert(tk.END, "="*80 + "\n", "error_header")
                
                # Configure error tags
                self.script_output.tag_config("error_bold", foreground="#ff0000", font=('Consolas', 9, 'bold'))
                self.script_output.tag_config("error", foreground="#ff8800")
                self.script_output.tag_config("error_header", foreground="#ff8800")
            
            self.script_output.see(tk.END)
            
        except Exception as e:
            # If message generation fails, show simple message
            output_dir = self.script_output_entry.get().strip() if hasattr(self, 'script_output_entry') else "output/custom_scripts"
            if success:
                messagebox.showinfo("✅ Execution Complete", 
                                  f"Script execution completed successfully!\n\n"
                                  f"Output directory: {os.path.abspath(output_dir)}\n\n"
                                  f"Check the output area above for details.")
            else:
                messagebox.showwarning("⚠️ Execution Complete", 
                                      f"Script execution completed with errors.\n\n"
                                      f"Output directory: {os.path.abspath(output_dir)}\n\n"
                                      f"Check the output area above for error details.")
    
    def stop_script_execution(self):
        """Stop script execution (placeholder - actual implementation would require process management)"""
        if self.script_executing:
            messagebox.showinfo("Info", "Script execution cannot be forcefully stopped. Please wait for completion.")
        else:
            messagebox.showinfo("Info", "No script is currently executing.")
    
    def create_log_tab(self, notebook):
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="Logs")
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=30)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        
    def check_emulator_connection(self):
        self.log("Checking for Android emulator connection...")
        devices = self.adb.list_devices()
        
        if devices:
            self.connected_device = devices[0]
            self.log(f"Connected to device: {self.connected_device}")
            self.update_device_info()
            self.update_root_status()
        else:
            self.connected_device = None
            self.log("No Android device/emulator found. Please start an emulator.")
            self.update_root_status()
            messagebox.showwarning("No Device", "No Android device or emulator detected.\nPlease start an Android emulator and try again.")
            
    def list_all_devices(self):
        devices = self.adb.list_devices()
        self.log(f"Found {len(devices)} device(s): {', '.join(devices) if devices else 'None'}")
        self.update_device_info()
        
    def get_device_info(self):
        if not self.connected_device:
            messagebox.showwarning("No Device", "No device connected")
            return
            
        info = self.adb.get_device_info(self.connected_device)
        self.device_info_text.delete(1.0, tk.END)
        self.device_info_text.insert(tk.END, json.dumps(info, indent=2))
        self.log("Device information retrieved")
        
    def update_device_info(self):
        if self.connected_device:
            info = self.adb.get_device_info(self.connected_device)
            self.device_info_text.delete(1.0, tk.END)
            self.device_info_text.insert(tk.END, json.dumps(info, indent=2))
            self.update_root_status()
            
    def update_root_status(self):
        """Update root status display"""
        if not self.connected_device:
            self.root_status_label.config(text="Root Status: No Device", fg='#888888')
            self.enable_root_btn.config(state=tk.DISABLED)
            self.disable_root_btn.config(state=tk.DISABLED)
            return
            
        # Refresh device connection first
        try:
            # Re-check devices to ensure connection is still valid
            devices = self.adb.list_devices()
            if self.connected_device not in devices:
                self.log("Device disconnected, reconnecting...")
                if devices:
                    self.connected_device = devices[0]
                else:
                    self.root_status_label.config(text="Root Status: Device Disconnected", fg='#ff0000')
                    return
        except:
            pass
            
        is_rooted = self.adb.check_root_status(self.connected_device)
        is_emulator = self.adb.is_emulator(self.connected_device)
        
        if is_rooted:
            self.root_status_label.config(text="Root Status: ✅ ROOTED", fg='#00ff00')
            self.enable_root_btn.config(state=tk.DISABLED)
            self.disable_root_btn.config(state=tk.NORMAL)
            self.log("✅ Root access confirmed")
        else:
            self.root_status_label.config(text="Root Status: ❌ Not Rooted", fg='#ff0000')
            if is_emulator:
                self.enable_root_btn.config(state=tk.NORMAL)
                self.enable_root_btn.config(text="Enable Root (Emulator)")
            else:
                self.enable_root_btn.config(state=tk.DISABLED)
                self.enable_root_btn.config(text="Enable Root (Physical Device - Not Supported)")
            self.disable_root_btn.config(state=tk.DISABLED)
            self.log("❌ Root access not available")
            
    def refresh_root_status(self):
        """Manually refresh root status"""
        self.log("Refreshing root status...")
        self.root_status_label.config(text="Root Status: Checking...", fg='#ffaa00')
        
        # Force reconnection check
        try:
            devices = self.adb.list_devices()
            if devices:
                if self.connected_device not in devices:
                    self.connected_device = devices[0]
                    self.log(f"Reconnected to device: {self.connected_device}")
        except Exception as e:
            self.log(f"Error refreshing connection: {str(e)}")
            
        self.update_root_status()
        self.log("Root status refreshed")
        
    def diagnose_root(self):
        """Diagnose root issues and show detailed information"""
        if not self.connected_device:
            messagebox.showwarning("No Device", "No device connected")
            return
            
        self.log("Running root diagnostics...")
        
        # Run diagnostics in thread
        thread = threading.Thread(target=self._diagnose_root_thread)
        thread.daemon = True
        thread.start()
        
    def _diagnose_root_thread(self):
        """Run root diagnostics"""
        try:
            diagnostics = []
            diagnostics.append("=== ROOT DIAGNOSTICS ===\n")
            diagnostics.append(f"Device: {self.connected_device}\n")
            diagnostics.append(f"Time: {datetime.now()}\n\n")
            
            # Check 1: Is it an emulator?
            is_emulator = self.adb.is_emulator(self.connected_device)
            diagnostics.append(f"1. Is Emulator: {is_emulator}\n")
            
            # Check 2: Current root status
            is_rooted = self.adb.check_root_status(self.connected_device)
            diagnostics.append(f"2. Current Root Status: {'ROOTED ✅' if is_rooted else 'NOT ROOTED ❌'}\n\n")
            
            # Check 3: Try adb root command
            diagnostics.append("3. Testing 'adb root' command:\n")
            output, success = self.adb._run_command('root', self.connected_device)
            diagnostics.append(f"   Command: adb root\n")
            diagnostics.append(f"   Success: {success}\n")
            diagnostics.append(f"   Output: {output if output else '(no output)'}\n\n")
            
            # Check 4: Check debuggable property
            diagnostics.append("4. Checking if emulator supports root:\n")
            debuggable, _ = self.adb.shell_command(self.connected_device, 'getprop ro.debuggable')
            diagnostics.append(f"   ro.debuggable: {debuggable}\n")
            diagnostics.append(f"   Supports root: {'YES ✅' if debuggable.strip() == '1' else 'NO ❌ (Try different system image)'}\n\n")
            
            # Check 5: Check kernel qemu (emulator indicator)
            qemu, _ = self.adb.shell_command(self.connected_device, 'getprop ro.kernel.qemu')
            diagnostics.append(f"5. Emulator check (ro.kernel.qemu): {qemu}\n\n")
            
            # Check 6: Try shell id
            diagnostics.append("6. Testing shell access:\n")
            id_output, id_success = self.adb.shell_command(self.connected_device, 'id')
            diagnostics.append(f"   Command: adb shell id\n")
            diagnostics.append(f"   Output: {id_output if id_output else '(no output)'}\n")
            diagnostics.append(f"   Is root (uid=0): {'YES ✅' if 'uid=0' in id_output else 'NO ❌'}\n\n")
            
            # Check 7: Try su command
            diagnostics.append("7. Testing su command:\n")
            su_output, su_success = self.adb.shell_command(self.connected_device, 'su -c id')
            diagnostics.append(f"   Command: adb shell su -c id\n")
            diagnostics.append(f"   Success: {su_success}\n")
            diagnostics.append(f"   Output: {su_output if su_output else '(no output)'}\n\n")
            
            # Recommendations
            diagnostics.append("=== RECOMMENDATIONS ===\n")
            if debuggable.strip() != '1':
                diagnostics.append("❌ This emulator doesn't support root.\n")
                diagnostics.append("   → Create new AVD with 'Google APIs' system image\n")
                diagnostics.append("   → Or use: emulator -avd YOUR_AVD -selinux permissive\n\n")
            elif not is_rooted:
                diagnostics.append("✅ Emulator supports root, but root is not enabled.\n")
                diagnostics.append("   → Try: adb root (in Command Prompt)\n")
                diagnostics.append("   → Then: adb kill-server && adb start-server\n")
                diagnostics.append("   → Then click 'Refresh Root Status' in tool\n\n")
            else:
                diagnostics.append("✅ Root is enabled and working!\n\n")
            
            # Show diagnostics
            result = "\n".join(diagnostics)
            self.log(result)
            self.root.after(0, lambda: self._show_diagnostics(result))
            
        except Exception as e:
            error_msg = f"Error running diagnostics: {str(e)}"
            self.log(error_msg)
            self.root.after(0, lambda: messagebox.showerror("Diagnostics Error", error_msg))
            
    def _show_diagnostics(self, diagnostics):
        """Show diagnostics in a window"""
        # Create new window for diagnostics
        diag_window = tk.Toplevel(self.root)
        diag_window.title("Root Diagnostics")
        diag_window.geometry("700x600")
        
        text_widget = scrolledtext.ScrolledText(diag_window, wrap=tk.WORD, font=('Courier', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, diagnostics)
        text_widget.config(state=tk.DISABLED)
        
        ttk.Button(diag_window, text="Close", command=diag_window.destroy).pack(pady=5)
            
    def enable_root_access(self):
        """Enable root access on device"""
        if not self.connected_device:
            messagebox.showwarning("No Device", "No device connected")
            return
            
        # Check if it's an emulator
        is_emulator = self.adb.is_emulator(self.connected_device)
        if not is_emulator:
            result = messagebox.askyesno(
                "Physical Device",
                "This appears to be a physical device.\n"
                "Root access cannot be enabled via ADB on physical devices.\n"
                "You need to root the device manually.\n\n"
                "Do you want to try anyway?"
            )
            if not result:
                return
                
        self.log("Attempting to enable root access...")
        self.root_status_label.config(text="Root Status: Enabling...", fg='#ffaa00')
        
        # Run in thread to avoid blocking
        thread = threading.Thread(target=self._enable_root_thread)
        thread.daemon = True
        thread.start()
        
    def _enable_root_thread(self):
        """Enable root in background thread"""
        try:
            result = self.adb.enable_root(self.connected_device)
            
            # Handle tuple return (success, message) or boolean
            if isinstance(result, tuple):
                success, message = result
            else:
                success = result
                message = "Root enabled" if success else "Root enable failed"
            
            if success:
                self.root_status_label.config(text="Root Status: ✅ ROOTED", fg='#00ff00')
                self.log(f"✅ Root access enabled successfully! {message}")
                self.root.after(0, lambda: messagebox.showinfo("Root Enabled", f"Root access has been enabled successfully!\n\n{message}\n\nYou can now access protected data and perform advanced monitoring."))
                self.update_device_info()
            else:
                self.root_status_label.config(text="Root Status: ❌ Failed", fg='#ff0000')
                self.log(f"❌ Failed to enable root access: {message}")
                
                # Provide detailed troubleshooting
                troubleshooting = f"""Failed to enable root access.

{message}

Troubleshooting Steps:
1. Make sure emulator is fully booted (home screen visible)
2. Try in Command Prompt:
   adb root
   adb kill-server
   adb start-server
   adb shell id
   (Should show uid=0 if root works)

3. Some emulators need root-enabled system images:
   - Create new AVD with system image that supports root
   - Or start emulator with: emulator -avd YOUR_AVD -selinux permissive

4. Check if emulator supports root:
   adb shell getprop ro.debuggable
   (Should return '1' for root-capable emulators)

5. Try restarting the emulator and try again"""
                
                self.root.after(0, lambda: messagebox.showerror("Root Failed", troubleshooting))
                self.update_root_status()
        except Exception as e:
            self.log(f"Error enabling root: {str(e)}")
            error_msg = f"Error enabling root: {str(e)}\n\nTry enabling root manually via Command Prompt:\nadb root\nadb kill-server\nadb start-server"
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
            self.update_root_status()
            
    def disable_root_access(self):
        """Disable root access"""
        if not self.connected_device:
            messagebox.showwarning("No Device", "No device connected")
            return
            
        result = messagebox.askyesno("Disable Root", "Are you sure you want to disable root access?")
        if not result:
            return
            
        self.log("Disabling root access...")
        self.root_status_label.config(text="Root Status: Disabling...", fg='#ffaa00')
        
        thread = threading.Thread(target=self._disable_root_thread)
        thread.daemon = True
        thread.start()
        
    def _disable_root_thread(self):
        """Disable root in background thread"""
        try:
            success = self.adb.disable_root(self.connected_device)
            
            if success:
                self.root_status_label.config(text="Root Status: ❌ Not Rooted", fg='#ff0000')
                self.log("Root access disabled")
                messagebox.showinfo("Root Disabled", "Root access has been disabled.")
                self.update_device_info()
            else:
                self.log("Failed to disable root access")
                messagebox.showerror("Error", "Failed to disable root access.")
                self.update_root_status()
        except Exception as e:
            self.log(f"Error disabling root: {str(e)}")
            messagebox.showerror("Error", f"Error disabling root: {str(e)}")
            self.update_root_status()
            
    def list_installed_apps(self):
        if not self.connected_device:
            messagebox.showwarning("No Device", "No device connected")
            return
            
        self.log("Fetching installed applications...")
        apps = self.adb.get_installed_packages(self.connected_device)
        
        self.apps_listbox.delete(0, tk.END)
        for app in apps:
            self.apps_listbox.insert(tk.END, app)
            
        self.log(f"Found {len(apps)} installed applications")
        
    def on_app_select(self, event):
        selection = self.apps_listbox.curselection()
        if selection:
            package = self.apps_listbox.get(selection[0])
            self.package_entry.delete(0, tk.END)
            self.package_entry.insert(0, package)
            # Update the selected package label
            self.selected_package_label.config(text=f"Selected package: {package}", foreground="white")
    
    def on_package_entry_change(self, event=None):
        """Update the selected package label when user types in the package entry"""
        package = self.package_entry.get().strip()
        if package:
            self.selected_package_label.config(text=f"Selected package: {package}", foreground="white")
        else:
            self.selected_package_label.config(text="Selected package: None", foreground="gray")
            
    def select_extraction_output_dir(self):
        """Select output directory for data extraction"""
        directory = filedialog.askdirectory(title="Select Output Directory for Extracted Data")
        if directory:
            self.extraction_output_entry.delete(0, tk.END)
            self.extraction_output_entry.insert(0, directory)
            self.log(f"Extraction output directory set to: {directory}")
    
    def select_sdcard_output_dir(self):
        """Select output directory for SDCard extraction"""
        directory = filedialog.askdirectory(title="Select Output Directory for SDCard Media")
        if directory:
            self.sdcard_output_entry.delete(0, tk.END)
            self.sdcard_output_entry.insert(0, directory)
            self.log(f"SDCard output directory set to: {directory}")
            
    def start_extraction(self):
        package = self.package_entry.get().strip()
        if not package:
            messagebox.showwarning("Invalid Input", "Please select a package from the list or enter a package name")
            return
            
        if not self.connected_device:
            messagebox.showwarning("No Device", "No device connected")
            return
        
        # Check root status - extraction requires root
        is_rooted = self.adb.check_root_status(self.connected_device)
        if not is_rooted:
            result = messagebox.askyesno(
                "⚠️ Root Access Required",
                "Root access is NOT enabled!\n\n"
                "Extracting data from app directories requires root access.\n"
                "Without root, extraction will likely fail.\n\n"
                "Please go to the Connection tab and click 'Enable Root (Emulator)' first.\n\n"
                "Do you want to try extraction anyway?"
            )
            if not result:
                return
        
        # Get the user-selected output directory
        extraction_output = self.extraction_output_entry.get().strip()
        if not extraction_output:
            messagebox.showwarning("Invalid Output", "Please select an output directory for the extracted data")
            return
        
        # Confirm extraction with user
        root_status = "✅ Root: Enabled" if is_rooted else "⚠️ Root: NOT Enabled"
        confirm_msg = (
            f"📦 Package: {package}\n\n"
            f"📁 Output Location:\n{os.path.abspath(extraction_output)}\n\n"
            f"{root_status}\n\n"
            f"All available data from this package will be extracted:\n"
            f"• Databases\n• Shared Preferences\n• Cache\n• Internal Storage\n• Logs\n\n"
            f"Proceed with extraction?"
        )
        if not messagebox.askyesno("Confirm Package Extraction", confirm_msg):
            return
            
        # Run extraction in thread
        thread = threading.Thread(target=self.extract_data, args=(package, extraction_output))
        thread.daemon = True
        thread.start()
        
    def extract_data(self, package, output_directory):
        # Show extraction in progress dialog
        self.root.after(0, lambda: self._show_extraction_progress(package))
        
        self.log(f"{'='*60}")
        self.log(f"🚀 Starting data extraction for package: {package}")
        self.log(f"📁 Output directory: {os.path.abspath(output_directory)}")
        self.log(f"{'='*60}")
        
        self._update_extraction_status("Running diagnostics...")
        
        # First, run diagnostic to check what's accessible
        self.log(f"🔍 Running diagnostic on /data/data/{package}...")
        diag = self.extractor.diagnose_app_directory(self.connected_device, package)
        
        self.log(f"🔐 ADB running as root: {diag.get('adb_root', False)}")
        self.log(f"🔐 SU command works: {diag.get('su_works', False)}")
        
        if diag['exists']:
            self.log(f"✅ App directory exists. Contents:")
            for line in diag['contents'][:15]:
                self.log(f"   {line}")
        else:
            self.log(f"⚠️ Could not access app directory.")
            for err in diag.get('errors', []):
                self.log(f"   Error: {err}")
        
        # Extract ALL available data for the selected package
        options = {
            'messages': True,
            'contacts': True,
            'calls': True,
            'media': True,
            'databases': True,
            'logs': True,
            'shared_prefs': True,
            'cache': True,
            'internal_storage': True
        }
        
        try:
            # Create the output directory if it doesn't exist
            os.makedirs(output_directory, exist_ok=True)
            
            self._update_extraction_status("Extracting databases...")
            self.log("📂 Extracting databases...")
            
            # Pass progress callback to extractor
            results = self.extractor.extract_app_data(
                self.connected_device, package, options, output_directory,
                progress_callback=self._update_extraction_status
            )
            output_path = results.get('output_path', output_directory)
            
            self._update_extraction_status("Finalizing...")
            
            # Build summary message
            extracted_items = results.get('extracted', {})
            root_access = results.get('root_access', False)
            errors = results.get('errors', [])
            
            summary_lines = [f"{'✅' if root_access else '⚠️'} Data extraction completed!\n\n"]
            summary_lines.append(f"📦 Package: {package}\n")
            summary_lines.append(f"📁 Output: {os.path.abspath(output_path)}\n")
            summary_lines.append(f"🔐 Root Access: {'Yes' if root_access else 'No'}\n\n")
            summary_lines.append("Extracted data:\n")
            
            found_count = 0
            total_files = 0
            for item_type, item_data in extracted_items.items():
                if isinstance(item_data, list) and item_data:
                    file_count = len(item_data)
                    total_files += file_count
                    summary_lines.append(f"  ✓ {item_type} ({file_count} files)\n")
                    found_count += 1
                elif isinstance(item_data, dict) and item_data:
                    summary_lines.append(f"  ✓ {item_type}\n")
                    found_count += 1
                else:
                    summary_lines.append(f"  ⚪ {item_type} (no data)\n")
            
            summary_lines.append(f"\n📊 Total: {found_count} categories, {total_files} files extracted")
            
            if errors:
                summary_lines.append(f"\n\n⚠️ Warnings:\n")
                for err in errors[:3]:
                    summary_lines.append(f"  • {err}\n")
            
            if not root_access:
                summary_lines.append(f"\n\n💡 Tip: Enable root access in Connection tab for full extraction")
            
            summary = "".join(summary_lines)
            
            self.log(f"{'='*60}")
            self.log(f"✅ Extraction completed. Results saved to {output_path}")
            self.log(f"📊 Total files extracted: {total_files}")
            self.log(f"{'='*60}")
            
            self.root.after(0, self._hide_extraction_progress)
            self.root.after(100, lambda: messagebox.showinfo(
                "Extraction Complete", 
                summary
            ))
        except Exception as e:
            self.log(f"❌ Extraction error: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            self.root.after(0, self._hide_extraction_progress)
            self.root.after(100, lambda: messagebox.showerror("Extraction Error", str(e)))
    
    def _show_extraction_progress(self, package):
        """Show extraction progress window"""
        self.progress_window = tk.Toplevel(self.root)
        self.progress_window.title("Extracting Data...")
        self.progress_window.geometry("400x150")
        self.progress_window.transient(self.root)
        self.progress_window.grab_set()
        self.progress_window.resizable(False, False)
        
        # Center the window
        self.progress_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 200
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 75
        self.progress_window.geometry(f"+{x}+{y}")
        
        # Content
        frame = ttk.Frame(self.progress_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text=f"📦 Extracting data from:", font=('Arial', 10)).pack(pady=(0, 5))
        ttk.Label(frame, text=package, font=('Arial', 11, 'bold')).pack(pady=(0, 15))
        
        self.progress_status_label = ttk.Label(frame, text="Initializing...", font=('Arial', 9))
        self.progress_status_label.pack(pady=(0, 10))
        
        # Progress bar (indeterminate)
        self.progress_bar = ttk.Progressbar(frame, mode='indeterminate', length=300)
        self.progress_bar.pack(pady=5)
        self.progress_bar.start(10)
        
        self.progress_window.protocol("WM_DELETE_WINDOW", lambda: None)  # Prevent closing
    
    def _update_extraction_status(self, status):
        """Update the extraction progress status"""
        self.log(f"   ➤ {status}")
        if hasattr(self, 'progress_status_label') and self.progress_status_label.winfo_exists():
            self.root.after(0, lambda: self.progress_status_label.config(text=status))
    
    def _hide_extraction_progress(self):
        """Hide the extraction progress window"""
        if hasattr(self, 'progress_bar'):
            self.progress_bar.stop()
        if hasattr(self, 'progress_window') and self.progress_window.winfo_exists():
            self.progress_window.destroy()
    
    def start_sdcard_extraction(self):
        """Start extraction of files from SDCard/external storage"""
        if not self.connected_device:
            messagebox.showwarning("No Device", "No device connected")
            return
        
        # Get the user-selected output directory for SDCard
        extraction_output = self.sdcard_output_entry.get().strip()
        if not extraction_output:
            messagebox.showwarning("Invalid Output", "Please select an output directory using the Browse button")
            return
        
        # Build list of folders to extract
        folders = []
        if self.extract_dcim.get():
            folders.append(("DCIM", "/sdcard/DCIM"))
        if self.extract_pictures.get():
            folders.append(("Pictures", "/sdcard/Pictures"))
        if self.extract_movies.get():
            folders.append(("Movies", "/sdcard/Movies"))
        if self.extract_downloads.get():
            folders.append(("Download", "/sdcard/Download"))
        if self.extract_documents.get():
            folders.append(("Documents", "/sdcard/Documents"))
        
        if not folders:
            messagebox.showwarning("Nothing Selected", "Please select at least one folder to extract")
            return
        
        folder_names = ", ".join([f[0] for f in folders])
        confirm_msg = (
            f"📷 Extract media from SDCard\n\n"
            f"Folders: {folder_names}\n\n"
            f"📁 Output Location:\n{os.path.abspath(extraction_output)}\n\n"
            f"No root required for this extraction.\n\n"
            f"Proceed?"
        )
        if not messagebox.askyesno("Confirm SDCard Extraction", confirm_msg):
            return
        
        # Run extraction in thread
        thread = threading.Thread(target=self._extract_sdcard_data, args=(folders, extraction_output))
        thread.daemon = True
        thread.start()
    
    def _extract_sdcard_data(self, folders, output_directory):
        """Extract data from SDCard folders"""
        self.root.after(0, lambda: self._show_extraction_progress("SDCard Media"))
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(output_directory, f"sdcard_extraction_{timestamp}")
        os.makedirs(output_dir, exist_ok=True)
        
        self.log(f"{'='*60}")
        self.log(f"📷 Starting SDCard extraction")
        self.log(f"📁 Output: {os.path.abspath(output_dir)}")
        self.log(f"{'='*60}")
        
        total_files = 0
        results = {}
        
        for folder_name, remote_path in folders:
            self._update_extraction_status(f"Extracting {folder_name}...")
            self.log(f"📂 Extracting {folder_name} from {remote_path}...")
            
            local_folder = os.path.join(output_dir, folder_name)
            os.makedirs(local_folder, exist_ok=True)
            
            # Check if folder exists on device
            check_output, _ = self.adb.shell_command(self.connected_device, f'ls -la {remote_path} 2>/dev/null')
            
            if check_output and 'No such file' not in check_output:
                # Pull the entire folder
                try:
                    # Use adb pull for the folder
                    import subprocess
                    cmd = [self.adb.adb_path, '-s', self.connected_device, 'pull', remote_path + '/.', local_folder]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                    
                    # Count files pulled
                    file_count = 0
                    for root, dirs, files in os.walk(local_folder):
                        file_count += len(files)
                    
                    total_files += file_count
                    results[folder_name] = file_count
                    self.log(f"   ✅ {folder_name}: {file_count} files extracted")
                except Exception as e:
                    self.log(f"   ❌ Error extracting {folder_name}: {str(e)}")
                    results[folder_name] = 0
            else:
                self.log(f"   ⚪ {folder_name}: folder not found or empty")
                results[folder_name] = 0
        
        self._update_extraction_status("Finalizing...")
        
        # Save extraction report
        report = {
            'extraction_type': 'sdcard',
            'timestamp': timestamp,
            'output_path': output_dir,
            'folders': results,
            'total_files': total_files
        }
        
        report_path = os.path.join(output_dir, 'extraction_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log(f"{'='*60}")
        self.log(f"✅ SDCard extraction completed!")
        self.log(f"📊 Total files extracted: {total_files}")
        self.log(f"{'='*60}")
        
        # Build summary
        summary_lines = ["✅ SDCard Extraction Complete!\n\n"]
        summary_lines.append(f"📁 Output: {os.path.abspath(output_dir)}\n\n")
        summary_lines.append("Extracted folders:\n")
        for folder_name, count in results.items():
            if count > 0:
                summary_lines.append(f"  ✓ {folder_name}: {count} files\n")
            else:
                summary_lines.append(f"  ⚪ {folder_name}: empty/not found\n")
        summary_lines.append(f"\n📊 Total: {total_files} files extracted")
        
        summary = "".join(summary_lines)
        
        self.root.after(0, self._hide_extraction_progress)
        self.root.after(100, lambda: messagebox.showinfo("SDCard Extraction Complete", summary))
            
    def start_monitoring(self):
        package = self.monitor_package_entry.get().strip()
        if not package:
            messagebox.showwarning("Invalid Input", "Please enter a package name")
            return
            
        if not self.connected_device:
            messagebox.showwarning("No Device", "No device connected")
            return
            
        self.monitoring_active = True
        self.enhanced_monitoring_active = self.use_enhanced.get()
        self.ultra_monitoring_active = self.use_ultra.get()
        self.monitor_start_btn.config(state=tk.DISABLED)
        self.monitor_stop_btn.config(state=tk.NORMAL)
        
        self.monitor_output.delete(1.0, tk.END)
        self.monitor_events_list = []  # Clear previous events
        self.current_monitoring_package = package  # Store current package
        if self.ultra_monitoring_active:
            self.monitor_output.insert(tk.END, f"🔥 ULTRA Monitoring started for {package} at {datetime.now()}\n")
            self.monitor_output.insert(tk.END, "=" * 80 + "\n")
            self.monitor_output.insert(tk.END, "Monitoring EVERYTHING: Login | OTP | Files | Databases | Preferences | Intents | Broadcasts | Memory | CPU | Network | Activities | Services\n")
            self.monitor_output.insert(tk.END, "=" * 80 + "\n\n")
        else:
            self.monitor_output.insert(tk.END, f"🚀 Enhanced Monitoring started for {package} at {datetime.now()}\n")
            self.monitor_output.insert(tk.END, "=" * 80 + "\n")
            self.monitor_output.insert(tk.END, "Monitoring: Login Events | OTP Generation | File Changes | Database Updates | Network Activity\n")
            self.monitor_output.insert(tk.END, "=" * 80 + "\n\n")
        
        thread = threading.Thread(target=self.monitor_app_enhanced, args=(package,))
        thread.daemon = True
        thread.start()
        
    def monitor_app_enhanced(self, package):
        """Enhanced/Ultra monitoring with detailed event tracking"""
        self.log(f"Starting monitoring for {package}...")
        
        try:
            if self.ultra_monitoring_active:
                # Use ULTRA monitor - monitors EVERYTHING
                self.log("🔥 Starting ULTRA monitoring - capturing EVERY detail...")
                event_queue = self.ultra_monitor.start_ultra_monitoring(self.connected_device, package)
                
                # Process events from ultra monitor
                while self.monitoring_active:
                    try:
                        event_type, event_msg = event_queue.get(timeout=0.5)
                        self.root.after(0, self._add_monitor_event, event_type, event_msg)
                    except:
                        continue
                        
            elif self.enhanced_monitoring_active:
                # Use enhanced monitor with multiple monitoring threads
                import queue
                event_queue = queue.Queue()
                
                def network_monitor():
                    last_connections = set()
                    while self.monitoring_active:
                        try:
                            output, _ = self.adb.shell_command(self.connected_device, 'netstat -an')
                            current_connections = set()
                            for line in output.split('\n'):
                                if 'ESTABLISHED' in line or 'LISTEN' in line:
                                    current_connections.add(line.strip())
                            new_conns = current_connections - last_connections
                            for conn in new_conns:
                                event_queue.put(("[NETWORK]", f"🔗 New connection: {conn}"))
                            last_connections = current_connections
                            time.sleep(1)
                        except:
                            time.sleep(5)
                
                def filesystem_monitor():
                    app_data_dir = f'/data/data/{package}'
                    while self.monitoring_active:
                        try:
                            output, _ = self.adb.shell_command(self.connected_device, f'find {app_data_dir} -type f -mmin -0.1 2>/dev/null')
                            if output and output.strip():
                                for line in output.split('\n'):
                                    if line.strip():
                                        event_queue.put(("[FILESYSTEM]", f"📝 File modified: {line.strip()}"))
                            time.sleep(1)
                        except:
                            time.sleep(5)
                
                def logcat_monitor():
                    keywords = ['login', 'log in', 'authenticate', 'otp', 'verification', 'code', 'password', 'token']
                    while self.monitoring_active:
                        try:
                            output, _ = self.adb.shell_command(self.connected_device, f'logcat -d -t 20 | grep -i {package}')
                            if output:
                                for line in output.split('\n'):
                                    if line.strip():
                                        line_lower = line.lower()
                                        if any(kw in line_lower for kw in ['login', 'log in', 'sign in', 'authenticate']):
                                            event_queue.put(("[AUTH]", f"🔑 LOGIN EVENT: {line.strip()[:150]}"))
                                        elif any(kw in line_lower for kw in ['otp', 'verification code', 'verify', 'sms code']):
                                            code_match = re.search(r'(\d{4,8})', line)
                                            if code_match:
                                                event_queue.put(("[OTP]", f"📱 OTP DETECTED - Code pattern: {code_match.group(1)} - {line.strip()[:150]}"))
                                            else:
                                                event_queue.put(("[OTP]", f"📱 OTP EVENT: {line.strip()[:150]}"))
                                        elif 'password' in line_lower or 'token' in line_lower:
                                            event_queue.put(("[SECURITY]", f"🔐 CREDENTIAL EVENT: {line.strip()[:150]}"))
                            time.sleep(2)
                        except:
                            time.sleep(5)
                
                def database_monitor():
                    app_data_dir = f'/data/data/{package}'
                    db_path = f'{app_data_dir}/databases/'
                    last_sizes = {}
                    while self.monitoring_active:
                        try:
                            output, _ = self.adb.shell_command(self.connected_device, f'find {db_path} -name "*.db" 2>/dev/null')
                            if output:
                                for line in output.split('\n'):
                                    if line.strip():
                                        size_output, _ = self.adb.shell_command(self.connected_device, f'stat -c %s {line.strip()} 2>/dev/null || stat -f %z {line.strip()} 2>/dev/null')
                                        try:
                                            size = int(size_output.strip())
                                            db_file = line.strip()
                                            if db_file in last_sizes and last_sizes[db_file] != size:
                                                event_queue.put(("[DATABASE]", f"💾 Database changed: {os.path.basename(db_file)} ({size - last_sizes[db_file]:+d} bytes)"))
                                            last_sizes[db_file] = size
                                        except:
                                            pass
                            time.sleep(2)
                        except:
                            time.sleep(5)
                
                # Start all monitoring threads
                threads = [
                    threading.Thread(target=network_monitor, daemon=True),
                    threading.Thread(target=filesystem_monitor, daemon=True),
                    threading.Thread(target=logcat_monitor, daemon=True),
                    threading.Thread(target=database_monitor, daemon=True),
                ]
                
                for t in threads:
                    t.start()
                
                # Process events from queue
                while self.monitoring_active:
                    try:
                        event_type, event_msg = event_queue.get(timeout=0.5)
                        self.root.after(0, self._add_monitor_event, event_type, event_msg)
                    except:
                        continue
            else:
                # Use standard monitor
                for event in self.monitor.monitor_app(self.connected_device, package):
                    if not self.monitoring_active:
                        break
                    self.root.after(0, self._add_monitor_event, "[STANDARD]", event)
                    
        except Exception as e:
            self.log(f"Monitoring error: {str(e)}")
            messagebox.showerror("Monitoring Error", str(e))
        finally:
            self.monitoring_active = False
            self.enhanced_monitoring_active = False
            self.ultra_monitoring_active = False
            self.ultra_monitor.stop_monitoring()
            self.root.after(0, lambda: self.monitor_start_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.monitor_stop_btn.config(state=tk.DISABLED))
            
    def _add_monitor_event(self, event_type, event_msg):
        """Add event to monitor output with appropriate highlighting"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_msg = f"[{timestamp}] {event_msg}\n"
        
        # Store event for export
        event_data = {
            'timestamp': datetime.now().isoformat(),
            'time': timestamp,
            'type': event_type,
            'message': event_msg,
            'full_message': full_msg.strip()
        }
        self.monitor_events_list.append(event_data)
        
        # Determine tag based on event type
        tag = "NETWORK"
        if "[AUTH]" in event_type or "LOGIN" in event_msg.upper():
            tag = "LOGIN"
        elif "[OTP]" in event_type or "OTP" in event_msg.upper():
            tag = "OTP"
        elif "[SECURITY]" in event_type or "CREDENTIAL" in event_msg.upper() or "SENSITIVE" in event_msg.upper():
            tag = "SECURITY"
        elif "[FILESYSTEM]" in event_type or "FILE" in event_type:
            tag = "FILESYSTEM"
        elif "[DATABASE]" in event_type or "DB" in event_type or "SQL" in event_msg.upper():
            tag = "DATABASE"
        elif "[ACTIVITY]" in event_type:
            tag = "ACTIVITY"
        elif "[SERVICE]" in event_type:
            tag = "SERVICE"
        elif "[INTENT]" in event_type:
            tag = "INTENT"
        elif "[BROADCAST]" in event_type:
            tag = "BROADCAST"
        elif "[PROVIDER]" in event_type:
            tag = "PROVIDER"
        elif "[MEMORY]" in event_type:
            tag = "MEMORY"
        elif "[CPU]" in event_type:
            tag = "CPU"
        elif "[PREFERENCES]" in event_type or "PREF" in event_type:
            tag = "PREFERENCES"
        elif "[API]" in event_type:
            tag = "API"
            
        self.monitor_output.insert(tk.END, full_msg, tag)
        self.monitor_output.see(tk.END)
        self.log(f"Monitor: {event_msg}")
            
    def stop_monitoring(self):
        self.monitoring_active = False
        self.enhanced_monitoring_active = False
        self.ultra_monitoring_active = False
        self.ultra_monitor.stop_monitoring()
        self.log("Monitoring stopped")
        self.monitor_output.insert(tk.END, f"\n{'='*80}\n")
        self.monitor_output.insert(tk.END, f"⏹️ Monitoring stopped at {datetime.now()}\n")
        self.monitor_output.see(tk.END)
        
        # Enable export button if we have events
        if self.monitor_events_list:
            self.export_btn.config(state=tk.NORMAL)
        
    def select_export_folder(self):
        """Select folder for exporting monitoring data"""
        folder = filedialog.askdirectory(title="Select Folder to Save Monitoring Data")
        if folder:
            self.export_output_dir = folder
            self.export_dir_label.config(text=folder, foreground="white")
            self.log(f"Export folder selected: {folder}")
            
    def export_monitoring_data(self):
        """Export monitoring data to selected folder as ZIP"""
        if not self.export_output_dir:
            messagebox.showwarning("No Folder Selected", "Please select an export folder first.")
            return
            
        if not self.monitor_events_list:
            messagebox.showwarning("No Data", "No monitoring data to export. Start monitoring first.")
            return
            
        # Run export in thread
        thread = threading.Thread(target=self._export_monitoring_thread)
        thread.daemon = True
        thread.start()
        
    def _export_monitoring_thread(self):
        """Export monitoring data in background thread"""
        try:
            self.log("Starting export of monitoring data...")
            
            # Create export directory structure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            package_name = self.current_monitoring_package or "unknown_package"
            export_name = f"monitoring_{package_name}_{timestamp}"
            export_path = os.path.join(self.export_output_dir, export_name)
            os.makedirs(export_path, exist_ok=True)
            
            # 1. Save all events as JSON
            events_json = {
                'package': package_name,
                'device': self.connected_device,
                'start_time': self.monitor_events_list[0]['timestamp'] if self.monitor_events_list else None,
                'end_time': self.monitor_events_list[-1]['timestamp'] if self.monitor_events_list else None,
                'total_events': len(self.monitor_events_list),
                'monitoring_mode': 'ULTRA' if self.ultra_monitoring_active else ('ENHANCED' if self.enhanced_monitoring_active else 'STANDARD'),
                'events': self.monitor_events_list
            }
            
            json_path = os.path.join(export_path, "monitoring_events.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(events_json, f, indent=2, ensure_ascii=False)
            
            # 2. Save events as readable text file
            txt_path = os.path.join(export_path, "monitoring_events.txt")
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"AKTIS Forensic Tool - Monitoring Report\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Package: {package_name}\n")
                f.write(f"Device: {self.connected_device}\n")
                f.write(f"Monitoring Mode: {events_json['monitoring_mode']}\n")
                f.write(f"Start Time: {events_json['start_time']}\n")
                f.write(f"End Time: {events_json['end_time']}\n")
                f.write(f"Total Events: {len(self.monitor_events_list)}\n")
                f.write("=" * 80 + "\n\n")
                
                # Group events by type
                event_types = {}
                for event in self.monitor_events_list:
                    event_type = event['type']
                    if event_type not in event_types:
                        event_types[event_type] = []
                    event_types[event_type].append(event)
                
                f.write("EVENT SUMMARY BY TYPE:\n")
                f.write("-" * 80 + "\n")
                for event_type, events in sorted(event_types.items()):
                    f.write(f"{event_type}: {len(events)} events\n")
                f.write("\n" + "=" * 80 + "\n\n")
                
                f.write("DETAILED EVENT LOG:\n")
                f.write("-" * 80 + "\n\n")
                for event in self.monitor_events_list:
                    f.write(f"[{event['time']}] {event['type']} - {event['message']}\n")
            
            # 3. Save categorized events
            categories = {
                'AUTH': [],
                'OTP': [],
                'FILESYSTEM': [],
                'DATABASE': [],
                'NETWORK': [],
                'ACTIVITY': [],
                'MEMORY': [],
                'CPU': [],
                'OTHER': []
            }
            
            for event in self.monitor_events_list:
                event_type = event['type'].upper()
                if '[AUTH]' in event_type or 'LOGIN' in event['message'].upper():
                    categories['AUTH'].append(event)
                elif '[OTP]' in event_type or 'OTP' in event['message'].upper():
                    categories['OTP'].append(event)
                elif '[FILESYSTEM]' in event_type or 'FILE' in event_type:
                    categories['FILESYSTEM'].append(event)
                elif '[DATABASE]' in event_type:
                    categories['DATABASE'].append(event)
                elif '[NETWORK]' in event_type:
                    categories['NETWORK'].append(event)
                elif '[ACTIVITY]' in event_type:
                    categories['ACTIVITY'].append(event)
                elif '[MEMORY]' in event_type:
                    categories['MEMORY'].append(event)
                elif '[CPU]' in event_type:
                    categories['CPU'].append(event)
                else:
                    categories['OTHER'].append(event)
            
            # Save categorized files
            for category, events in categories.items():
                if events:
                    cat_path = os.path.join(export_path, f"events_{category.lower()}.txt")
                    with open(cat_path, 'w', encoding='utf-8') as f:
                        f.write(f"{category} EVENTS ({len(events)} total)\n")
                        f.write("=" * 80 + "\n\n")
                        for event in events:
                            f.write(f"[{event['time']}] {event['message']}\n")
            
            # 4. Save metadata
            metadata = {
                'export_time': datetime.now().isoformat(),
                'tool_version': 'AKTIS Forensic Tool for 4440',
                'package': package_name,
                'device': self.connected_device,
                'monitoring_mode': events_json['monitoring_mode'],
                'total_events': len(self.monitor_events_list),
                'event_breakdown': {cat: len(events) for cat, events in categories.items() if events}
            }
            
            metadata_path = os.path.join(export_path, "metadata.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            # 5. Create ZIP file
            zip_filename = f"{export_name}.zip"
            zip_path = os.path.join(self.export_output_dir, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(export_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, export_path)
                        zipf.write(file_path, arcname)
            
            # 6. Clean up temporary directory (optional - keep it for now)
            # shutil.rmtree(export_path)
            
            # Show success message
            self.root.after(0, lambda: messagebox.showinfo(
                "Export Complete",
                f"Monitoring data exported successfully!\n\n"
                f"ZIP File: {zip_filename}\n"
                f"Location: {self.export_output_dir}\n\n"
                f"Total Events: {len(self.monitor_events_list)}\n"
                f"Files Created: {len([f for f in os.listdir(export_path) if os.path.isfile(os.path.join(export_path, f))])}"
            ))
            
            self.log(f"✅ Export complete: {zip_path}")
            self.log(f"   Total events: {len(self.monitor_events_list)}")
            self.log(f"   Files in ZIP: {len([f for f in os.listdir(export_path) if os.path.isfile(os.path.join(export_path, f))])}")
            
        except Exception as e:
            error_msg = f"Error exporting data: {str(e)}"
            self.log(error_msg)
            self.root.after(0, lambda: messagebox.showerror("Export Error", error_msg))
        
    def start_analysis(self):
        package = self.analyze_package_entry.get().strip()
        if not package:
            messagebox.showwarning("Invalid Input", "Please enter a package name")
            return
            
        if not self.connected_device:
            messagebox.showwarning("No Device", "No device connected")
            return
            
        thread = threading.Thread(target=self.analyze_app, args=(package,))
        thread.daemon = True
        thread.start()
        
    def analyze_app(self, package):
        self.log(f"Starting analysis for {package}...")
        self.analysis_results.delete(1.0, tk.END)
        self.analysis_results.insert(tk.END, f"Analyzing {package}...\n\n")
        
        options = {
            'permissions': self.analyze_permissions.get(),
            'network': self.analyze_network.get(),
            'security': self.analyze_security.get(),
            'vulnerabilities': self.analyze_vulnerabilities.get()
        }
        
        try:
            results = self.analyzer.analyze_app(self.connected_device, package, options)
            self.analysis_results.delete(1.0, tk.END)
            self.analysis_results.insert(tk.END, json.dumps(results, indent=2))
            self.log("Analysis completed")
            messagebox.showinfo("Analysis Complete", "Analysis completed successfully!")
        except Exception as e:
            self.log(f"Analysis error: {str(e)}")
            messagebox.showerror("Analysis Error", str(e))


def main():
    root = tk.Tk()
    app = ForensicToolGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
