"""
Enhanced App Monitor Module
Monitors even the slightest app updates including login events, OTP generation, etc.
"""

import time
import re
import json
import os
from datetime import datetime


class EnhancedMonitor:
    def __init__(self):
        self.adb = None
        self.monitoring = False
        self.last_file_states = {}
        self.last_db_states = {}
        self.last_prefs_states = {}
        
    def set_adb(self, adb_connector):
        """Set ADB connector"""
        self.adb = adb_connector
        
    def monitor_app_enhanced(self, device, package):
        """Enhanced monitoring with detailed event tracking"""
        self.monitoring = True
        
        # Start all monitoring threads
        import threading
        
        threads = [
            threading.Thread(target=self._monitor_network_enhanced, args=(device, package), daemon=True),
            threading.Thread(target=self._monitor_filesystem_enhanced, args=(device, package), daemon=True),
            threading.Thread(target=self._monitor_databases_enhanced, args=(device, package), daemon=True),
            threading.Thread(target=self._monitor_preferences, args=(device, package), daemon=True),
            threading.Thread(target=self._monitor_logcat_events, args=(device, package), daemon=True),
            threading.Thread(target=self._monitor_activities, args=(device, package), daemon=True),
            threading.Thread(target=self._monitor_services, args=(device, package), daemon=True),
        ]
        
        for thread in threads:
            thread.start()
            
        # Yield events from all monitors
        while self.monitoring:
            time.sleep(0.5)  # Small delay to prevent CPU spinning
            yield None  # Events are handled in threads and passed via callback
            
    def _monitor_network_enhanced(self, device, package):
        """Enhanced network monitoring with detailed connection info"""
        last_connections = set()
        
        while self.monitoring:
            try:
                # Get detailed network info
                output, _ = self.adb.shell_command(device, 'netstat -an')
                current_connections = set()
                
                for line in output.split('\n'):
                    if 'ESTABLISHED' in line or 'LISTEN' in line or 'SYN_SENT' in line:
                        current_connections.add(line.strip())
                        
                # Detect new connections
                new_conns = current_connections - last_connections
                for conn in new_conns:
                    # Extract IP and port
                    ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+):(\d+)', conn)
                    if ip_match:
                        ip, port = ip_match.groups()
                        yield f"[NETWORK] 🔗 New connection to {ip}:{port} - {conn}"
                        
                # Detect closed connections
                closed_conns = last_connections - current_connections
                for conn in closed_conns:
                    yield f"[NETWORK] ❌ Connection closed: {conn}"
                    
                last_connections = current_connections
                time.sleep(1)  # Check every second
                
            except Exception as e:
                yield f"[NETWORK] ⚠️ Error: {str(e)}"
                time.sleep(5)
                
    def _monitor_filesystem_enhanced(self, device, package):
        """Monitor file system changes with timestamps"""
        app_data_dir = f'/data/data/{package}'
        
        while self.monitoring:
            try:
                # Monitor all file changes (even seconds old)
                output, _ = self.adb.shell_command(device, f'find {app_data_dir} -type f -mmin -0.1 2>/dev/null')
                
                if output and output.strip():
                    for line in output.split('\n'):
                        if line.strip():
                            file_path = line.strip()
                            # Get file modification time
                            stat_output, _ = self.adb.shell_command(device, f'stat -c %y {file_path} 2>/dev/null || stat -f "%Sm" {file_path} 2>/dev/null')
                            
                            # Check if file is new or modified
                            if file_path not in self.last_file_states:
                                yield f"[FILESYSTEM] ✨ NEW FILE: {file_path}"
                            else:
                                yield f"[FILESYSTEM] 📝 MODIFIED: {file_path} (Time: {stat_output.strip()})"
                                
                            self.last_file_states[file_path] = datetime.now().isoformat()
                            
                # Monitor directory creation
                dir_output, _ = self.adb.shell_command(device, f'find {app_data_dir} -type d -mmin -0.1 2>/dev/null')
                if dir_output and dir_output.strip():
                    for line in dir_output.split('\n'):
                        if line.strip():
                            yield f"[FILESYSTEM] 📁 NEW DIRECTORY: {line.strip()}"
                            
                time.sleep(1)  # Check every second
                
            except Exception as e:
                yield f"[FILESYSTEM] ⚠️ Error: {str(e)}"
                time.sleep(5)
                
    def _monitor_databases_enhanced(self, device, package):
        """Monitor database changes"""
        app_data_dir = f'/data/data/{package}'
        db_path = f'{app_data_dir}/databases/'
        
        while self.monitoring:
            try:
                # List all databases
                output, _ = self.adb.shell_command(device, f'find {db_path} -name "*.db" 2>/dev/null')
                
                if output:
                    current_dbs = {}
                    for line in output.split('\n'):
                        if line.strip():
                            db_file = line.strip()
                            # Get database size
                            size_output, _ = self.adb.shell_command(device, f'stat -c %s {db_file} 2>/dev/null || stat -f %z {db_file} 2>/dev/null')
                            try:
                                size = int(size_output.strip())
                                current_dbs[db_file] = size
                                
                                # Check if size changed
                                if db_file in self.last_db_states:
                                    if self.last_db_states[db_file] != size:
                                        size_diff = size - self.last_db_states[db_file]
                                        yield f"[DATABASE] 💾 {os.path.basename(db_file)} changed: {size_diff:+d} bytes (New size: {size} bytes)"
                                else:
                                    yield f"[DATABASE] ✨ NEW DATABASE: {os.path.basename(db_file)} ({size} bytes)"
                                    
                            except:
                                pass
                                
                    self.last_db_states.update(current_dbs)
                    
                time.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                yield f"[DATABASE] ⚠️ Error: {str(e)}"
                time.sleep(5)
                
    def _monitor_preferences(self, device, package):
        """Monitor shared preferences changes"""
        app_data_dir = f'/data/data/{package}'
        prefs_path = f'{app_data_dir}/shared_prefs/'
        
        while self.monitoring:
            try:
                # Monitor preference files
                output, _ = self.adb.shell_command(device, f'find {prefs_path} -name "*.xml" -mmin -0.1 2>/dev/null')
                
                if output and output.strip():
                    for line in output.split('\n'):
                        if line.strip():
                            prefs_file = line.strip()
                            if prefs_file not in self.last_prefs_states:
                                yield f"[PREFERENCES] ⚙️ NEW PREFERENCE FILE: {os.path.basename(prefs_file)}"
                            else:
                                yield f"[PREFERENCES] ⚙️ MODIFIED: {os.path.basename(prefs_file)}"
                                
                            # Try to read preference content for key changes
                            content, _ = self.adb.shell_command(device, f'cat {prefs_file} 2>/dev/null')
                            if content:
                                # Look for common patterns
                                if 'password' in content.lower() or 'token' in content.lower():
                                    yield f"[PREFERENCES] 🔐 SECURITY: {os.path.basename(prefs_file)} contains sensitive data"
                                    
                            self.last_prefs_states[prefs_file] = datetime.now().isoformat()
                            
                time.sleep(1)
                
            except Exception as e:
                yield f"[PREFERENCES] ⚠️ Error: {str(e)}"
                time.sleep(5)
                
    def _monitor_logcat_events(self, device, package):
        """Monitor logcat for specific events like login, OTP, etc."""
        keywords = [
            'login', 'log in', 'authenticate', 'auth', 'sign in',
            'otp', 'verification', 'verify', 'code', 'password',
            'token', 'session', 'credential', 'user', 'account'
        ]
        
        last_log_position = 0
        
        while self.monitoring:
            try:
                # Get recent logcat entries
                output, _ = self.adb.shell_command(device, f'logcat -d -t 50 | grep -i {package}')
                
                if output:
                    lines = output.split('\n')
                    for line in lines:
                        if line.strip():
                            line_lower = line.lower()
                            
                            # Check for login events
                            if any(kw in line_lower for kw in ['login', 'log in', 'sign in', 'authenticate']):
                                yield f"[AUTH] 🔑 LOGIN EVENT: {line.strip()[:100]}"
                                
                            # Check for OTP/verification
                            if any(kw in line_lower for kw in ['otp', 'verification code', 'verify', 'sms code']):
                                # Try to extract code
                                code_match = re.search(r'(\d{4,8})', line)
                                if code_match:
                                    yield f"[OTP] 📱 OTP DETECTED: Code pattern found - {line.strip()[:100]}"
                                else:
                                    yield f"[OTP] 📱 OTP EVENT: {line.strip()[:100]}"
                                    
                            # Check for password/token events
                            if 'password' in line_lower or 'token' in line_lower:
                                yield f"[SECURITY] 🔐 CREDENTIAL EVENT: {line.strip()[:100]}"
                                
                            # Check for network requests
                            if 'http' in line_lower or 'api' in line_lower:
                                yield f"[API] 🌐 API CALL: {line.strip()[:100]}"
                                
                time.sleep(2)
                
            except Exception as e:
                yield f"[LOGCAT] ⚠️ Error: {str(e)}"
                time.sleep(5)
                
    def _monitor_activities(self, device, package):
        """Monitor activity launches"""
        last_activities = set()
        
        while self.monitoring:
            try:
                # Get current activities
                output, _ = self.adb.shell_command(device, f'dumpsys activity activities | grep -A 5 {package}')
                
                if output:
                    # Extract activity names
                    activity_matches = re.findall(r'([a-zA-Z0-9._]+/[a-zA-Z0-9._]+)', output)
                    current_activities = set(activity_matches)
                    
                    # Detect new activities
                    new_activities = current_activities - last_activities
                    for activity in new_activities:
                        yield f"[ACTIVITY] 🚀 LAUNCHED: {activity}"
                        
                    last_activities = current_activities
                    
                time.sleep(2)
                
            except Exception as e:
                yield f"[ACTIVITY] ⚠️ Error: {str(e)}"
                time.sleep(5)
                
    def _monitor_services(self, device, package):
        """Monitor service starts/stops"""
        last_services = set()
        
        while self.monitoring:
            try:
                # Get running services
                output, _ = self.adb.shell_command(device, f'dumpsys activity services {package}')
                
                if output:
                    # Extract service names
                    service_matches = re.findall(r'ServiceRecord\{[^}]+\} ([a-zA-Z0-9._]+/[a-zA-Z0-9._]+)', output)
                    current_services = set(service_matches)
                    
                    # Detect new services
                    new_services = current_services - last_services
                    for service in new_services:
                        yield f"[SERVICE] ⚙️ STARTED: {service}"
                        
                    # Detect stopped services
                    stopped_services = last_services - current_services
                    for service in stopped_services:
                        yield f"[SERVICE] ⏹️ STOPPED: {service}"
                        
                    last_services = current_services
                    
                time.sleep(3)
                
            except Exception as e:
                yield f"[SERVICE] ⚠️ Error: {str(e)}"
                time.sleep(5)
                
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False

