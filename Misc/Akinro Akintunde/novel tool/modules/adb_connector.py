"""
ADB Connector Module
Handles connection and communication with Android devices/emulators via ADB
"""

import subprocess
import json
import re
import os
import shutil
import time


class ADBConnector:
    def __init__(self):
        self.adb_path = self._find_adb()
        
    def _find_adb(self):
        """Find ADB executable in common locations"""
        adb = shutil.which('adb')
        if adb:
            return adb
        # Try common Android SDK paths
        common_paths = [
            'C:\\Users\\%USERNAME%\\AppData\\Local\\Android\\Sdk\\platform-tools\\adb.exe',
            'C:\\Android\\platform-tools\\adb.exe',
            'adb'  # Fallback to system PATH
        ]
        for path in common_paths:
            expanded = os.path.expandvars(path)
            if os.path.exists(expanded):
                return expanded
        return 'adb'  # Assume it's in PATH
        
    def _run_command(self, command, device=None):
        """Execute ADB command"""
        try:
            if device:
                cmd = [self.adb_path, '-s', device] + command.split()
            else:
                cmd = [self.adb_path] + command.split()
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.stdout.strip(), result.returncode == 0
        except Exception as e:
            return str(e), False
            
    def list_devices(self):
        """List all connected Android devices/emulators"""
        output, success = self._run_command('devices')
        if not success:
            return []
            
        devices = []
        lines = output.split('\n')[1:]  # Skip header
        for line in lines:
            if line.strip():
                device_id = line.split('\t')[0]
                if device_id:
                    devices.append(device_id)
                    
        return devices
        
    def get_device_info(self, device):
        """Get detailed information about a device"""
        info = {}
        
        # Get device model
        model, _ = self._run_command('shell getprop ro.product.model', device)
        info['model'] = model
        
        # Get Android version
        version, _ = self._run_command('shell getprop ro.build.version.release', device)
        info['android_version'] = version
        
        # Get SDK version
        sdk, _ = self._run_command('shell getprop ro.build.version.sdk', device)
        info['sdk_version'] = sdk
        
        # Get device manufacturer
        manufacturer, _ = self._run_command('shell getprop ro.product.manufacturer', device)
        info['manufacturer'] = manufacturer
        
        # Get device name
        device_name, _ = self._run_command('shell getprop ro.product.device', device)
        info['device_name'] = device_name
        
        # Get serial number
        serial, _ = self._run_command('get-serialno', device)
        info['serial'] = serial
        
        # Check if rooted
        root_check, _ = self._run_command('shell su -c id', device)
        info['rooted'] = 'uid=0' in root_check
        
        return info
        
    def get_installed_packages(self, device):
        """Get list of installed packages"""
        output, success = self._run_command('shell pm list packages', device)
        if not success:
            return []
            
        packages = []
        for line in output.split('\n'):
            if line.startswith('package:'):
                packages.append(line.replace('package:', '').strip())
                
        return sorted(packages)
        
    def get_package_info(self, device, package):
        """Get detailed information about a package"""
        output, success = self._run_command(f'shell dumpsys package {package}', device)
        if not success:
            return {}
            
        info = {}
        # Parse package info from dumpsys output
        if 'versionName' in output:
            version_match = re.search(r'versionName=([^\s]+)', output)
            if version_match:
                info['version'] = version_match.group(1)
                
        if 'userId' in output:
            uid_match = re.search(r'userId=(\d+)', output)
            if uid_match:
                info['uid'] = uid_match.group(1)
                
        return info
        
    def pull_file(self, device, remote_path, local_path):
        """Pull a file from device to local system"""
        output, success = self._run_command(f'pull {remote_path} {local_path}', device)
        return success
        
    def push_file(self, device, local_path, remote_path):
        """Push a file from local system to device"""
        output, success = self._run_command(f'push {local_path} {remote_path}', device)
        return success
        
    def shell_command(self, device, command):
        """Execute shell command on device"""
        output, success = self._run_command(f'shell {command}', device)
        return output, success
        
    def check_root_status(self, device):
        """Check if device has root access - multiple methods"""
        # Method 1: Check if adbd is running as root
        output, success = self._run_command('root', device)
        if success and ('running as root' in output.lower() or 'already running as root' in output.lower()):
            return True
        
        # Method 2: Try su command
        output, success = self._run_command('shell su -c id', device)
        if success and 'uid=0' in output:
            return True
        
        # Method 3: Try su with echo
        output, success = self._run_command('shell su -c "echo root"', device)
        if success and 'root' in output.lower() and 'not found' not in output.lower():
            return True
        
        # Method 4: Check whoami as root
        output, success = self._run_command('shell su -c whoami', device)
        if success and 'root' in output.lower():
            return True
        
        # Method 5: Direct shell check (for adb root mode)
        output, success = self._run_command('shell id', device)
        if success and 'uid=0' in output:
            return True
            
        return False
        
    def enable_root(self, device):
        """Enable root access on device (works for emulators)"""
        # For emulators, use adb root
        output, success = self._run_command('root', device)
        
        if success:
            # Restart ADB server to apply root
            self._run_command('kill-server', device)
            time.sleep(1)
            self._run_command('start-server', device)
            time.sleep(2)
            
            # Verify root is enabled
            return self.check_root_status(device)
        
        return False
        
    def disable_root(self, device):
        """Disable root access (restart as non-root)"""
        output, success = self._run_command('unroot', device)
        
        if success:
            # Restart ADB server
            self._run_command('kill-server', device)
            time.sleep(1)
            self._run_command('start-server', device)
            time.sleep(2)
            return True
        
        return False
        
    def is_emulator(self, device):
        """Check if device is an emulator"""
        output, success = self._run_command('shell getprop ro.kernel.qemu', device)
        if success and output.strip() == '1':
            return True
        
        # Alternative check
        output, success = self._run_command('shell getprop ro.hardware', device)
        return success and 'goldfish' in output.lower()

