"""
Ultra-Detailed Monitor Module
Monitors EVERY possible detail including intents, broadcasts, content providers, memory, CPU, etc.
"""

import time
import re
import os
import json
import queue
from datetime import datetime


class UltraMonitor:
    def __init__(self):
        self.adb = None
        self.monitoring = False
        self.event_queue = queue.Queue()
        self.last_states = {
            'files': {},
            'databases': {},
            'preferences': {},
            'processes': {},
            'memory': {},
            'network': set(),
        }
        
    def set_adb(self, adb_connector):
        """Set ADB connector"""
        self.adb = adb_connector
        
    def start_ultra_monitoring(self, device, package):
        """Start comprehensive monitoring of every detail"""
        self.monitoring = True
        
        import threading
        
        # Start all monitoring threads
        monitors = [
            ('logcat_stream', self._monitor_logcat_stream),
            ('filesystem_detailed', self._monitor_filesystem_detailed),
            ('database_content', self._monitor_database_content),
            ('preferences_content', self._monitor_preferences_content),
            ('intents', self._monitor_intents),
            ('broadcasts', self._monitor_broadcasts),
            ('content_providers', self._monitor_content_providers),
            ('memory_usage', self._monitor_memory),
            ('cpu_usage', self._monitor_cpu),
            ('network_packets', self._monitor_network_detailed),
            ('clipboard', self._monitor_clipboard),
            ('activities_detailed', self._monitor_activities_detailed),
            ('services_detailed', self._monitor_services_detailed),
            ('file_content_changes', self._monitor_file_content),
        ]
        
        threads = []
        for name, monitor_func in monitors:
            thread = threading.Thread(
                target=monitor_func,
                args=(device, package),
                name=name,
                daemon=True
            )
            thread.start()
            threads.append(thread)
            
        return self.event_queue
        
    def _monitor_logcat_stream(self, device, package):
        """Continuous logcat streaming - captures EVERY log entry"""
        while self.monitoring:
            try:
                # Stream logcat continuously
                output, _ = self.adb.shell_command(device, f'logcat -v time | grep {package}')
                if output:
                    for line in output.split('\n'):
                        if line.strip() and package in line:
                            # Analyze every log line
                            self._analyze_log_line(line, package)
                time.sleep(0.5)  # Very frequent checks
            except:
                time.sleep(1)
                
    def _analyze_log_line(self, line, package):
        """Deep analysis of each log line"""
        line_lower = line.lower()
        
        # Login detection
        login_patterns = ['login', 'sign in', 'authenticate', 'auth', 'session', 'logged in', 'user login']
        if any(p in line_lower for p in login_patterns):
            self.event_queue.put(("[AUTH]", f"🔑 LOGIN: {line.strip()}"))
            
        # OTP detection with pattern matching
        otp_patterns = [
            r'(\d{4,8})',  # 4-8 digit codes
            r'code[:\s]+(\d+)',
            r'verification[:\s]+(\d+)',
            r'otp[:\s]+(\d+)',
            r'sms[:\s]+code[:\s]+(\d+)',
        ]
        for pattern in otp_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                self.event_queue.put(("[OTP]", f"📱 OTP CODE: {match.group(1)} - {line.strip()[:200]}"))
                break
                
        # Password/token detection
        if any(kw in line_lower for kw in ['password', 'token', 'credential', 'secret', 'key']):
            # Try to extract (but mask sensitive parts)
            masked = re.sub(r'([pP]assword|token|key)[:=]\s*([^\s]+)', r'\1=***MASKED***', line)
            self.event_queue.put(("[SECURITY]", f"🔐 CREDENTIAL: {masked.strip()[:200]}"))
            
        # API calls
        if 'http' in line_lower or 'api' in line_lower or 'request' in line_lower:
            self.event_queue.put(("[API]", f"🌐 API CALL: {line.strip()[:200]}"))
            
        # Database operations
        if any(kw in line_lower for kw in ['insert', 'update', 'delete', 'select', 'sql']):
            self.event_queue.put(("[DATABASE]", f"💾 SQL OPERATION: {line.strip()[:200]}"))
            
        # File operations
        if any(kw in line_lower for kw in ['file', 'write', 'read', 'save', 'load']):
            self.event_queue.put(("[FILESYSTEM]", f"📁 FILE OP: {line.strip()[:200]}"))
            
    def _monitor_filesystem_detailed(self, device, package):
        """Monitor filesystem with content tracking"""
        app_data_dir = f'/data/data/{package}'
        
        while self.monitoring:
            try:
                # Monitor ALL files, not just modified
                output, _ = self.adb.shell_command(device, f'find {app_data_dir} -type f 2>/dev/null')
                
                if output:
                    current_files = {}
                    for file_path in output.split('\n'):
                        if file_path.strip():
                            # Get file hash/size for change detection
                            stat_cmd = f'stat -c "%s %Y" {file_path} 2>/dev/null || stat -f "%z %m" {file_path} 2>/dev/null'
                            stat_output, _ = self.adb.shell_command(device, stat_cmd)
                            
                            if stat_output:
                                try:
                                    size, mtime = stat_output.strip().split()[:2]
                                    file_key = file_path.strip()
                                    
                                    if file_key in self.last_states['files']:
                                        old_size, old_mtime = self.last_states['files'][file_key]
                                        if size != old_size or mtime != old_mtime:
                                            self.event_queue.put(("[FILESYSTEM]", f"📝 FILE CHANGED: {os.path.basename(file_path)} (Size: {old_size}→{size}, Modified: {mtime})"))
                                    else:
                                        self.event_queue.put(("[FILESYSTEM]", f"✨ NEW FILE: {os.path.basename(file_path)} ({size} bytes)"))
                                    
                                    current_files[file_key] = (size, mtime)
                                except:
                                    pass
                                    
                    self.last_states['files'] = current_files
                    
                time.sleep(0.5)  # Check every 0.5 seconds
            except:
                time.sleep(2)
                
    def _monitor_database_content(self, device, package):
        """Monitor database content changes, not just size"""
        app_data_dir = f'/data/data/{package}'
        db_path = f'{app_data_dir}/databases/'
        
        while self.monitoring:
            try:
                output, _ = self.adb.shell_command(device, f'find {db_path} -name "*.db" 2>/dev/null')
                
                if output:
                    for db_file in output.split('\n'):
                        if db_file.strip():
                            # Get table count and row counts
                            try:
                                # Try to get database info
                                tables_cmd = f'sqlite3 {db_file.strip()} ".tables" 2>/dev/null'
                                tables_output, _ = self.adb.shell_command(device, tables_cmd)
                                
                                if tables_output and db_file.strip() not in self.last_states['databases']:
                                    self.event_queue.put(("[DATABASE]", f"💾 NEW DB: {os.path.basename(db_file)} (Tables: {len(tables_output.split())})"))
                                    
                                # Track database modifications
                                size_cmd = f'stat -c %s {db_file.strip()} 2>/dev/null || stat -f %z {db_file.strip()} 2>/dev/null'
                                size_output, _ = self.adb.shell_command(device, size_cmd)
                                
                                if size_output:
                                    size = int(size_output.strip())
                                    if db_file.strip() in self.last_states['databases']:
                                        if self.last_states['databases'][db_file.strip()] != size:
                                            diff = size - self.last_states['databases'][db_file.strip()]
                                            self.event_queue.put(("[DATABASE]", f"💾 DB MODIFIED: {os.path.basename(db_file)} ({diff:+d} bytes, new size: {size})"))
                                    self.last_states['databases'][db_file.strip()] = size
                            except:
                                pass
                                
                time.sleep(1)
            except:
                time.sleep(3)
                
    def _monitor_preferences_content(self, device, package):
        """Monitor shared preferences content changes"""
        app_data_dir = f'/data/data/{package}'
        prefs_path = f'{app_data_dir}/shared_prefs/'
        
        while self.monitoring:
            try:
                output, _ = self.adb.shell_command(device, f'find {prefs_path} -name "*.xml" 2>/dev/null')
                
                if output:
                    for prefs_file in output.split('\n'):
                        if prefs_file.strip():
                            # Read preference content
                            content, _ = self.adb.shell_command(device, f'cat {prefs_file.strip()} 2>/dev/null')
                            
                            if content:
                                file_key = prefs_file.strip()
                                
                                # Check for changes
                                if file_key in self.last_states['preferences']:
                                    if self.last_states['preferences'][file_key] != content:
                                        # Extract key-value changes
                                        old_keys = set(re.findall(r'name="([^"]+)"', self.last_states['preferences'][file_key]))
                                        new_keys = set(re.findall(r'name="([^"]+)"', content))
                                        
                                        added = new_keys - old_keys
                                        if added:
                                            self.event_queue.put(("[PREFERENCES]", f"⚙️ NEW PREF: {os.path.basename(prefs_file)} - Keys: {', '.join(added)}"))
                                        
                                        # Check for sensitive data
                                        if any(kw in content.lower() for kw in ['password', 'token', 'key', 'secret', 'auth']):
                                            self.event_queue.put(("[SECURITY]", f"🔐 SENSITIVE PREF: {os.path.basename(prefs_file)} contains credentials"))
                                else:
                                    # New preference file
                                    keys = re.findall(r'name="([^"]+)"', content)
                                    self.event_queue.put(("[PREFERENCES]", f"⚙️ NEW PREF FILE: {os.path.basename(prefs_file)} ({len(keys)} keys)"))
                                    
                                self.last_states['preferences'][file_key] = content
                                
                time.sleep(1)
            except:
                time.sleep(3)
                
    def _monitor_intents(self, device, package):
        """Monitor intents sent/received by app"""
        while self.monitoring:
            try:
                # Monitor intent broadcasts
                output, _ = self.adb.shell_command(device, f'dumpsys activity broadcasts | grep {package}')
                
                if output:
                    # Extract intent actions
                    actions = re.findall(r'Action: ([^\s]+)', output)
                    for action in actions:
                        self.event_queue.put(("[INTENT]", f"📨 INTENT: {action}"))
                        
                time.sleep(2)
            except:
                time.sleep(5)
                
    def _monitor_broadcasts(self, device, package):
        """Monitor broadcast receivers"""
        while self.monitoring:
            try:
                output, _ = self.adb.shell_command(device, f'dumpsys activity broadcasts | grep -A 5 {package}')
                
                if output:
                    # Look for broadcast patterns
                    if 'BroadcastRecord' in output:
                        self.event_queue.put(("[BROADCAST]", f"📡 BROADCAST: {package} received broadcast"))
                        
                time.sleep(2)
            except:
                time.sleep(5)
                
    def _monitor_content_providers(self, device, package):
        """Monitor content provider access"""
        while self.monitoring:
            try:
                output, _ = self.adb.shell_command(device, f'dumpsys activity providers | grep {package}')
                
                if output:
                    providers = re.findall(r'([a-zA-Z0-9._]+/[a-zA-Z0-9._]+)', output)
                    for provider in providers:
                        self.event_queue.put(("[PROVIDER]", f"📦 CONTENT PROVIDER: {provider}"))
                        
                time.sleep(3)
            except:
                time.sleep(5)
                
    def _monitor_memory(self, device, package):
        """Monitor memory usage"""
        while self.monitoring:
            try:
                output, _ = self.adb.shell_command(device, f'dumpsys meminfo {package}')
                
                if output:
                    # Extract memory info
                    pss_match = re.search(r'TOTAL\s+(\d+)', output)
                    if pss_match:
                        pss = int(pss_match.group(1))
                        if package in self.last_states['memory']:
                            old_pss = self.last_states['memory'][package]
                            if abs(pss - old_pss) > 1024:  # Significant change (>1MB)
                                self.event_queue.put(("[MEMORY]", f"🧠 MEMORY CHANGE: {package} ({old_pss//1024}MB → {pss//1024}MB)"))
                        self.last_states['memory'][package] = pss
                        
                time.sleep(3)
            except:
                time.sleep(5)
                
    def _monitor_cpu(self, device, package):
        """Monitor CPU usage"""
        while self.monitoring:
            try:
                output, _ = self.adb.shell_command(device, f'top -n 1 | grep {package}')
                
                if output:
                    # Extract CPU percentage
                    cpu_match = re.search(r'(\d+\.?\d*)%', output)
                    if cpu_match:
                        cpu = float(cpu_match.group(1))
                        if cpu > 10:  # Significant CPU usage
                            self.event_queue.put(("[CPU]", f"⚡ HIGH CPU: {package} ({cpu}%)"))
                            
                time.sleep(2)
            except:
                time.sleep(5)
                
    def _monitor_network_detailed(self, device, package):
        """Detailed network monitoring"""
        while self.monitoring:
            try:
                # Get detailed network stats
                output, _ = self.adb.shell_command(device, f'cat /proc/net/tcp | grep -E ":[0-9A-F]+"')
                
                # Also check network connections
                netstat_output, _ = self.adb.shell_command(device, 'netstat -an')
                
                current_connections = set()
                for line in netstat_output.split('\n'):
                    if 'ESTABLISHED' in line or 'LISTEN' in line:
                        current_connections.add(line.strip())
                        
                # Detect new connections
                new_conns = current_connections - self.last_states['network']
                for conn in new_conns:
                    # Extract IP and port
                    ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+):(\d+)', conn)
                    if ip_match:
                        ip, port = ip_match.groups()
                        self.event_queue.put(("[NETWORK]", f"🔗 NEW CONNECTION: {ip}:{port} - {conn[:100]}"))
                        
                self.last_states['network'] = current_connections
                time.sleep(1)
            except:
                time.sleep(3)
                
    def _monitor_clipboard(self, device, package):
        """Monitor clipboard access (if accessible)"""
        while self.monitoring:
            try:
                # Try to get clipboard content
                output, _ = self.adb.shell_command(device, 'service call clipboard 1')
                # This is limited but we try
                time.sleep(5)
            except:
                time.sleep(10)
                
    def _monitor_activities_detailed(self, device, package):
        """Detailed activity monitoring"""
        last_activities = set()
        
        while self.monitoring:
            try:
                output, _ = self.adb.shell_command(device, f'dumpsys activity activities | grep -A 10 {package}')
                
                if output:
                    activities = re.findall(r'([a-zA-Z0-9._]+/[a-zA-Z0-9._]+)', output)
                    current_activities = set(activities)
                    
                    new_activities = current_activities - last_activities
                    for activity in new_activities:
                        self.event_queue.put(("[ACTIVITY]", f"🚀 ACTIVITY LAUNCHED: {activity}"))
                        
                    last_activities = current_activities
                    
                time.sleep(1)
            except:
                time.sleep(3)
                
    def _monitor_services_detailed(self, device, package):
        """Detailed service monitoring"""
        last_services = set()
        
        while self.monitoring:
            try:
                output, _ = self.adb.shell_command(device, f'dumpsys activity services {package}')
                
                if output:
                    services = re.findall(r'ServiceRecord\{[^}]+\} ([a-zA-Z0-9._]+/[a-zA-Z0-9._]+)', output)
                    current_services = set(services)
                    
                    new_services = current_services - last_services
                    for service in new_services:
                        self.event_queue.put(("[SERVICE]", f"⚙️ SERVICE STARTED: {service}"))
                        
                    stopped = last_services - current_services
                    for service in stopped:
                        self.event_queue.put(("[SERVICE]", f"⏹️ SERVICE STOPPED: {service}"))
                        
                    last_services = current_services
                    
                time.sleep(2)
            except:
                time.sleep(5)
                
    def _monitor_file_content(self, device, package):
        """Monitor actual file content changes (for text files)"""
        app_data_dir = f'/data/data/{package}'
        
        while self.monitoring:
            try:
                # Monitor key files for content changes
                key_files = [
                    f'{app_data_dir}/shared_prefs/*.xml',
                    f'{app_data_dir}/files/*.txt',
                    f'{app_data_dir}/files/*.json',
                    f'{app_data_dir}/files/*.log',
                ]
                
                for pattern in key_files:
                    output, _ = self.adb.shell_command(device, f'find {pattern.replace("*", "")} -type f -mmin -0.1 2>/dev/null')
                    if output:
                        for file_path in output.split('\n'):
                            if file_path.strip():
                                # Try to read content
                                content, _ = self.adb.shell_command(device, f'head -20 {file_path.strip()} 2>/dev/null')
                                if content:
                                    self.event_queue.put(("[FILESYSTEM]", f"📄 FILE CONTENT: {os.path.basename(file_path)} - {content[:100]}..."))
                                    
                time.sleep(2)
            except:
                time.sleep(5)
                
    def stop_monitoring(self):
        """Stop all monitoring"""
        self.monitoring = False

