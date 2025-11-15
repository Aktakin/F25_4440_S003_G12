"""
Analyzer Module (MobSF-like)
Analyzes app security, permissions, and vulnerabilities
"""

import re
import json


class Analyzer:
    def __init__(self):
        self.adb = None
        
    def set_adb(self, adb_connector):
        """Set ADB connector"""
        self.adb = adb_connector
        
    def analyze_app(self, device, package, options):
        """Perform comprehensive app analysis"""
        results = {
            'package': package,
            'analysis': {}
        }
        
        # Permissions analysis
        if options.get('permissions'):
            results['analysis']['permissions'] = self.analyze_permissions(device, package)
            
        # Network analysis
        if options.get('network'):
            results['analysis']['network'] = self.analyze_network(device, package)
            
        # Security analysis
        if options.get('security'):
            results['analysis']['security'] = self.analyze_security(device, package)
            
        # Vulnerability scan
        if options.get('vulnerabilities'):
            results['analysis']['vulnerabilities'] = self.scan_vulnerabilities(device, package)
            
        return results
        
    def analyze_permissions(self, device, package):
        """Analyze app permissions"""
        output, _ = self.adb.shell_command(device, f'dumpsys package {package}')
        
        permissions = {
            'granted': [],
            'requested': [],
            'dangerous': []
        }
        
        dangerous_perms = [
            'INTERNET', 'READ_SMS', 'SEND_SMS', 'READ_PHONE_STATE',
            'ACCESS_FINE_LOCATION', 'ACCESS_COARSE_LOCATION',
            'READ_CONTACTS', 'WRITE_CONTACTS', 'READ_CALENDAR',
            'WRITE_CALENDAR', 'CAMERA', 'RECORD_AUDIO',
            'READ_EXTERNAL_STORAGE', 'WRITE_EXTERNAL_STORAGE'
        ]
        
        for line in output.split('\n'):
            if 'permission' in line.lower():
                # Check if granted
                if 'granted=true' in line:
                    match = re.search(r'android\.permission\.(\w+)', line)
                    if match:
                        perm = match.group(1)
                        permissions['granted'].append(perm)
                        if perm in dangerous_perms:
                            permissions['dangerous'].append(perm)
                            
                # Check if requested
                if 'requested' in line.lower():
                    match = re.search(r'android\.permission\.(\w+)', line)
                    if match:
                        perm = match.group(1)
                        if perm not in permissions['requested']:
                            permissions['requested'].append(perm)
                            
        return permissions
        
    def analyze_network(self, device, package):
        """Analyze network behavior"""
        # Get network connections
        output, _ = self.adb.shell_command(device, 'netstat -an')
        
        network_info = {
            'connections': [],
            'suspicious_activity': []
        }
        
        for line in output.split('\n'):
            if 'ESTABLISHED' in line or 'LISTEN' in line:
                network_info['connections'].append(line.strip())
                
                # Check for suspicious patterns
                if any(ip in line for ip in ['192.168.', '10.', '172.']):
                    network_info['suspicious_activity'].append(f"Local network connection: {line.strip()}")
                    
        return network_info
        
    def analyze_security(self, device, package):
        """Analyze security aspects"""
        security_info = {
            'debuggable': False,
            'backup_allowed': False,
            'root_detection': False,
            'certificate_info': None
        }
        
        # Check if app is debuggable
        output, _ = self.adb.shell_command(device, f'dumpsys package {package} | grep debuggable')
        security_info['debuggable'] = 'debuggable=true' in output.lower()
        
        # Check backup allowed
        output, _ = self.adb.shell_command(device, f'dumpsys package {package} | grep backup')
        security_info['backup_allowed'] = 'allowBackup=true' in output.lower()
        
        # Try to get package info
        pkg_info = self.adb.get_package_info(device, package)
        if pkg_info:
            security_info['package_info'] = pkg_info
            
        return security_info
        
    def scan_vulnerabilities(self, device, package):
        """Scan for common vulnerabilities"""
        vulnerabilities = []
        
        # Check for insecure data storage
        output, _ = self.adb.shell_command(device, f'dumpsys package {package}')
        
        if 'allowBackup=true' in output:
            vulnerabilities.append({
                'type': 'Insecure Backup',
                'severity': 'Medium',
                'description': 'App allows backup which may expose sensitive data'
            })
            
        # Check for debug mode
        if 'debuggable=true' in output:
            vulnerabilities.append({
                'type': 'Debug Mode Enabled',
                'severity': 'High',
                'description': 'App is debuggable, allowing potential code injection'
            })
            
        # Check permissions
        perms = self.analyze_permissions(device, package)
        if len(perms['dangerous']) > 5:
            vulnerabilities.append({
                'type': 'Excessive Permissions',
                'severity': 'Medium',
                'description': f'App requests {len(perms["dangerous"])} dangerous permissions'
            })
            
        return vulnerabilities

