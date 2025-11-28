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
    
    def _run_shell_command(self, device, shell_cmd):
        """Execute ADB shell command properly (handles complex commands with quotes)"""
        try:
            if device:
                cmd = [self.adb_path, '-s', device, 'shell', shell_cmd]
            else:
                cmd = [self.adb_path, 'shell', shell_cmd]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, shell=False)
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
    
    def pull_file_root(self, device, remote_path, local_path):
        """Pull a file from device using root access (for protected directories)"""
        # Use a temp location on /sdcard/ which is accessible without root for pulling
        temp_path = f'/sdcard/aktis_temp_{os.path.basename(remote_path)}'
        
        try:
            # Copy file to temp location using root
            copy_cmd = f'su -c "cp \\"{remote_path}\\" \\"{temp_path}\\""'
            output, success = self.shell_command(device, copy_cmd)
            
            if not success:
                # Try alternative cp syntax
                copy_cmd = f'su -c "cat \\"{remote_path}\\" > \\"{temp_path}\\""'
                output, success = self.shell_command(device, copy_cmd)
            
            # Make temp file readable
            chmod_cmd = f'su -c "chmod 644 \\"{temp_path}\\""'
            self.shell_command(device, chmod_cmd)
            
            # Pull from temp location
            pull_success = self.pull_file(device, temp_path, local_path)
            
            # Cleanup temp file
            rm_cmd = f'rm -f "{temp_path}"'
            self.shell_command(device, rm_cmd)
            
            return pull_success
        except Exception as e:
            return False
    
    def pull_directory_root(self, device, remote_dir, local_dir):
        """Pull entire directory from device using root access"""
        os.makedirs(local_dir, exist_ok=True)
        pulled_files = []
        
        # List all files in the directory
        list_cmd = f'su -c "find \\"{remote_dir}\\" -type f 2>/dev/null"'
        output, success = self.shell_command(device, list_cmd)
        
        if output:
            for line in output.split('\n'):
                remote_file = line.strip()
                if remote_file:
                    filename = os.path.basename(remote_file)
                    local_path = os.path.join(local_dir, filename)
                    if self.pull_file_root(device, remote_file, local_path):
                        pulled_files.append(local_path)
        
        return pulled_files
        
    def push_file(self, device, local_path, remote_path):
        """Push a file from local system to device"""
        output, success = self._run_command(f'push {local_path} {remote_path}', device)
        return success
        
    def shell_command(self, device, command):
        """Execute shell command on device"""
        # Use the proper shell command method for complex commands
        output, success = self._run_shell_command(device, command)
        return output, success
        
    def check_root_status(self, device):
        """Check if device has root access - multiple methods"""
        # Method 1: Check if adbd is running as root (non-destructive check)
        output, success = self._run_command('root', device)
        if output and ('running as root' in output.lower() or 'already running as root' in output.lower()):
            return True
        
        # Method 2: Direct shell check (for adb root mode) - fastest
        output, success = self._run_command('shell id', device)
        if success and output and 'uid=0' in output:
            return True
        
        # Method 3: Try su command
        output, success = self._run_command('shell su -c id', device)
        if success and output and 'uid=0' in output:
            return True
        
        # Method 4: Try su with echo
        output, success = self._run_command('shell su -c "echo root"', device)
        if success and output and 'root' in output.lower() and 'not found' not in output.lower() and 'permission denied' not in output.lower():
            return True
        
        # Method 5: Check whoami as root
        output, success = self._run_command('shell su -c whoami', device)
        if success and output and 'root' in output.lower():
            return True
            
        return False
        
    def enable_root(self, device):
        """Enable root access on device (works for emulators)"""
        # Check current root status first
        if self.check_root_status(device):
            return True, "Already running as root"  # Already rooted
        
        # For emulators, use adb root
        output, success = self._run_command('root', device)
        
        # Check output for error messages
        if output:
            output_lower = output.lower()
            if 'cannot run as root' in output_lower or 'production builds' in output_lower:
                # Emulator doesn't support root via adb root
                # Try alternative: check if emulator supports root at all
                return False, "This emulator/system image doesn't support root via 'adb root'. Try starting emulator with root-enabled system image."
            
            if 'already running as root' in output_lower or 'running as root' in output_lower:
                # Already in root mode, just need to reconnect
                success = True
            elif 'restarting adbd as root' in output_lower:
                # Root command worked, need to reconnect
                success = True
        
        if success or (output and 'restarting' in output.lower()):
            # Restart ADB server to apply root
            self._run_command('kill-server', device)
            time.sleep(2)  # Wait longer
            self._run_command('start-server', device)
            time.sleep(3)  # Wait longer for reconnection
            
            # Reconnect to device
            devices = self.list_devices()
            if device not in devices and devices:
                device = devices[0]  # Use first available device
            
            # Verify root is enabled
            if self.check_root_status(device):
                return True, "Root enabled successfully"
            else:
                # Root command ran but verification failed
                return False, f"Root command executed but verification failed. Output: {output}"
        
        return False, f"Failed to enable root. ADB output: {output}"
        
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

