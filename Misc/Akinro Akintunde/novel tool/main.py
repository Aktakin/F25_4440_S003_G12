#!/usr/bin/env python3
"""
Android Forensic Analysis Tool - AKT
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
        self.root.title("AKT Forensic Tool for 4440")
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
        
        self.create_header()
        self.create_widgets()
        self.check_emulator_connection()
        
    def create_header(self):
        """Create header with AKT logo and tagline"""
        header_frame = tk.Frame(self.root, bg='#2d2d2d', height=100)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # AKT Logo (Text-based)
        logo_frame = tk.Frame(header_frame, bg='#2d2d2d')
        logo_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Large AKT text
        logo_font = font.Font(family='Arial', size=36, weight='bold')
        logo_label = tk.Label(logo_frame, text="AKT", fg='#4a9eff', bg='#2d2d2d', font=logo_font)
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
        ttk.Button(app_frame, text="Get Installed Apps", command=self.list_installed_apps).grid(row=0, column=2, padx=5)
        
        # Apps List
        list_frame = ttk.Frame(extract_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ttk.Label(list_frame, text="Installed Applications:").pack(anchor=tk.W)
        self.apps_listbox = tk.Listbox(list_frame, height=10)
        self.apps_listbox.pack(fill=tk.BOTH, expand=True)
        self.apps_listbox.bind('<<ListboxSelect>>', self.on_app_select)
        
        # Extraction Options
        options_frame = ttk.LabelFrame(extract_frame, text="Extraction Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.extract_messages = tk.BooleanVar(value=True)
        self.extract_contacts = tk.BooleanVar(value=True)
        self.extract_calls = tk.BooleanVar(value=True)
        self.extract_media = tk.BooleanVar(value=True)
        self.extract_databases = tk.BooleanVar(value=True)
        self.extract_logs = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="Messages", variable=self.extract_messages).grid(row=0, column=0, padx=5, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Contacts", variable=self.extract_contacts).grid(row=0, column=1, padx=5, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Call Logs", variable=self.extract_calls).grid(row=0, column=2, padx=5, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Media Files", variable=self.extract_media).grid(row=1, column=0, padx=5, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Databases", variable=self.extract_databases).grid(row=1, column=1, padx=5, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Logs", variable=self.extract_logs).grid(row=1, column=2, padx=5, sticky=tk.W)
        
        # Extract Button
        ttk.Button(extract_frame, text="Extract Data", command=self.start_extraction).pack(pady=10)
        
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
            success = self.adb.enable_root(self.connected_device)
            
            if success:
                self.root_status_label.config(text="Root Status: ✅ ROOTED", fg='#00ff00')
                self.log("✅ Root access enabled successfully!")
                messagebox.showinfo("Root Enabled", "Root access has been enabled successfully!\n\nYou can now access protected data and perform advanced monitoring.")
                self.update_device_info()
            else:
                self.root_status_label.config(text="Root Status: ❌ Failed", fg='#ff0000')
                self.log("❌ Failed to enable root access")
                messagebox.showerror("Root Failed", "Failed to enable root access.\n\nFor emulators, make sure:\n- Emulator is running\n- ADB is properly connected\n\nFor physical devices, root must be enabled manually.")
                self.update_root_status()
        except Exception as e:
            self.log(f"Error enabling root: {str(e)}")
            messagebox.showerror("Error", f"Error enabling root: {str(e)}")
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
            
    def start_extraction(self):
        package = self.package_entry.get().strip()
        if not package:
            messagebox.showwarning("Invalid Input", "Please enter a package name")
            return
            
        if not self.connected_device:
            messagebox.showwarning("No Device", "No device connected")
            return
            
        # Run extraction in thread
        thread = threading.Thread(target=self.extract_data, args=(package,))
        thread.daemon = True
        thread.start()
        
    def extract_data(self, package):
        self.log(f"Starting data extraction for {package}...")
        
        options = {
            'messages': self.extract_messages.get(),
            'contacts': self.extract_contacts.get(),
            'calls': self.extract_calls.get(),
            'media': self.extract_media.get(),
            'databases': self.extract_databases.get(),
            'logs': self.extract_logs.get()
        }
        
        try:
            results = self.extractor.extract_app_data(self.connected_device, package, options, self.output_dir)
            self.log(f"Extraction completed. Results saved to {results.get('output_path', 'N/A')}")
            messagebox.showinfo("Extraction Complete", f"Data extracted successfully!\nSaved to: {results.get('output_path', 'N/A')}")
        except Exception as e:
            self.log(f"Extraction error: {str(e)}")
            messagebox.showerror("Extraction Error", str(e))
            
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
