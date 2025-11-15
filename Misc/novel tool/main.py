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
        self.monitor_events_list = []  # Store all events for export
        self.current_monitoring_package = None
        self.export_output_dir = None  # User-selected export directory
        
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
                f.write(f"AKT Forensic Tool - Monitoring Report\n")
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
                'tool_version': 'AKT Forensic Tool for 4440',
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
