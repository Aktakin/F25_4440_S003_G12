"""
App Monitor Module (MVT-like)
Monitors app behavior, network activity, and system events
"""

import time
import re


class AppMonitor:
    def __init__(self):
        self.adb = None
        self.monitoring = False
        
    def set_adb(self, adb_connector):
        """Set ADB connector"""
        self.adb = adb_connector
        
    def monitor_app(self, device, package):
        """Monitor app activity"""
        self.monitoring = True
        
        # Monitor network activity
        for event in self.monitor_network(device, package):
            if not self.monitoring:
                break
            yield event
            
        # Monitor file system access
        for event in self.monitor_filesystem(device, package):
            if not self.monitoring:
                break
            yield event
            
        # Monitor process activity
        for event in self.monitor_process(device, package):
            if not self.monitoring:
                break
            yield event
            
    def monitor_network(self, device, package):
        """Monitor network connections"""
        last_connections = set()
        
        while self.monitoring:
            try:
                # Get network connections
                output, _ = self.adb.shell_command(device, 'netstat -an')
                
                # Filter for connections related to the package
                lines = output.split('\n')
                current_connections = []
                
                for line in lines:
                    if 'ESTABLISHED' in line or 'LISTEN' in line:
                        # Try to match with package's network activity
                        if any(keyword in line for keyword in ['tcp', 'udp']):
                            current_connections.append(line.strip())
                            
                # Detect new connections
                new_connections = set(current_connections) - last_connections
                if new_connections:
                    for conn in new_connections:
                        yield f"[NETWORK] New connection: {conn}"
                        
                last_connections = set(current_connections)
                time.sleep(2)
                
            except Exception as e:
                yield f"[NETWORK] Error: {str(e)}"
                time.sleep(5)
                
    def monitor_filesystem(self, device, package):
        """Monitor file system access"""
        app_data_dir = f'/data/data/{package}'
        
        while self.monitoring:
            try:
                # Monitor file changes in app directory
                output, _ = self.adb.shell_command(device, f'find {app_data_dir} -type f -mmin -1 2>/dev/null')
                
                if output and output.strip():
                    for line in output.split('\n'):
                        if line.strip():
                            yield f"[FILESYSTEM] Modified file: {line.strip()}"
                            
                time.sleep(5)
                
            except Exception as e:
                yield f"[FILESYSTEM] Error: {str(e)}"
                time.sleep(5)
                
    def monitor_process(self, device, package):
        """Monitor process activity"""
        while self.monitoring:
            try:
                # Get process info
                output, _ = self.adb.shell_command(device, f'ps | grep {package}')
                
                if output:
                    lines = output.split('\n')
                    for line in lines:
                        if package in line and line.strip():
                            # Parse process info
                            parts = line.split()
                            if len(parts) >= 2:
                                pid = parts[1]
                                yield f"[PROCESS] PID {pid} active for {package}"
                                
                time.sleep(3)
                
            except Exception as e:
                yield f"[PROCESS] Error: {str(e)}"
                time.sleep(5)
                
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        
    def get_network_connections(self, device, package):
        """Get current network connections for package"""
        output, _ = self.adb.shell_command(device, 'netstat -an')
        connections = []
        
        for line in output.split('\n'):
            if 'ESTABLISHED' in line or 'LISTEN' in line:
                connections.append(line.strip())
                
        return connections
        
    def get_app_permissions(self, device, package):
        """Get app permissions"""
        output, _ = self.adb.shell_command(device, f'dumpsys package {package} | grep permission')
        permissions = []
        
        for line in output.split('\n'):
            if 'granted=true' in line or 'granted=false' in line:
                # Extract permission name
                match = re.search(r'android\.permission\.(\w+)', line)
                if match:
                    permissions.append(match.group(1))
                    
        return permissions

