#!/usr/bin/env python3
"""
Android Forensic Analysis Tool
Combines concepts from Andriller, MVT, and MobSF
Works with Android Emulator for app data extraction and monitoring
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import os
import json
from datetime import datetime

from modules.adb_connector import ADBConnector
from modules.data_extractor import DataExtractor
from modules.app_monitor import AppMonitor
from modules.analyzer import Analyzer


class ForensicToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Android Forensic Analysis Tool")
        self.root.geometry("1200x800")
        
        # Initialize modules
        self.adb = ADBConnector()
        self.extractor = DataExtractor()
        self.extractor.set_adb(self.adb)
        self.monitor = AppMonitor()
        self.monitor.set_adb(self.adb)
        self.analyzer = Analyzer()
        self.analyzer.set_adb(self.adb)
        
        # Variables
        self.connected_device = None
        self.monitoring_active = False
        self.output_dir = "output"
        
        self.create_widgets()
        self.check_emulator_connection()
        
    def create_widgets(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Connection Tab
        self.create_connection_tab(notebook)
        
        # Data Extraction Tab
        self.create_extraction_tab(notebook)
        
        # Monitoring Tab
        self.create_monitoring_tab(notebook)
        
        # Analysis Tab
        self.create_analysis_tab(notebook)
        
        # Log Tab
        self.create_log_tab(notebook)
        
    def create_connection_tab(self, notebook):
        conn_frame = ttk.Frame(notebook)
        notebook.add(conn_frame, text="Connection")
        
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
        notebook.add(monitor_frame, text="Monitoring")
        
        # Package Selection
        pkg_frame = ttk.LabelFrame(monitor_frame, text="Monitor Package", padding=10)
        pkg_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(pkg_frame, text="Package Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.monitor_package_entry = ttk.Entry(pkg_frame, width=40)
        self.monitor_package_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Monitoring Controls
        control_frame = ttk.Frame(monitor_frame)
        control_frame.pack(pady=10)
        
        self.monitor_start_btn = ttk.Button(control_frame, text="Start Monitoring", command=self.start_monitoring)
        self.monitor_start_btn.pack(side=tk.LEFT, padx=5)
        
        self.monitor_stop_btn = ttk.Button(control_frame, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED)
        self.monitor_stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Monitoring Output
        output_frame = ttk.LabelFrame(monitor_frame, text="Monitoring Output", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.monitor_output = scrolledtext.ScrolledText(output_frame, height=15)
        self.monitor_output.pack(fill=tk.BOTH, expand=True)
        
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
        else:
            self.connected_device = None
            self.log("No Android device/emulator found. Please start an emulator.")
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
        self.monitor_start_btn.config(state=tk.DISABLED)
        self.monitor_stop_btn.config(state=tk.NORMAL)
        
        thread = threading.Thread(target=self.monitor_app, args=(package,))
        thread.daemon = True
        thread.start()
        
    def monitor_app(self, package):
        self.log(f"Starting monitoring for {package}...")
        self.monitor_output.insert(tk.END, f"Monitoring started for {package} at {datetime.now()}\n")
        
        try:
            for event in self.monitor.monitor_app(self.connected_device, package):
                if not self.monitoring_active:
                    break
                    
                self.monitor_output.insert(tk.END, f"{event}\n")
                self.monitor_output.see(tk.END)
                self.log(f"Monitor event: {event}")
                
        except Exception as e:
            self.log(f"Monitoring error: {str(e)}")
            messagebox.showerror("Monitoring Error", str(e))
        finally:
            self.monitoring_active = False
            self.monitor_start_btn.config(state=tk.NORMAL)
            self.monitor_stop_btn.config(state=tk.DISABLED)
            
    def stop_monitoring(self):
        self.monitoring_active = False
        self.log("Monitoring stopped")
        self.monitor_output.insert(tk.END, f"Monitoring stopped at {datetime.now()}\n")
        
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

