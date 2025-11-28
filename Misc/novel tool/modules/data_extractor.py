"""
Data Extractor Module (Andriller-like)
Extracts data SPECIFIC to the selected Android app package
Requires ROOT access to extract from /data/data/{package}/
"""

import os
import json
import shutil
from datetime import datetime


class DataExtractor:
    def __init__(self):
        self.adb = None  # Will be set by main app
        
    def set_adb(self, adb_connector):
        """Set ADB connector"""
        self.adb = adb_connector
        
    def extract_app_data(self, device, package, options, output_base_dir, progress_callback=None):
        """Extract ALL data specific to the selected app package"""
        from modules.adb_connector import ADBConnector
        
        def update_progress(msg):
            if progress_callback:
                progress_callback(msg)
        
        # Get ADB connector if not set
        if not self.adb:
            self.adb = ADBConnector()
        
        update_progress("Checking root access...")
        
        # Check root status first
        is_rooted = self.adb.check_root_status(device)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(output_base_dir, package, timestamp)
        os.makedirs(output_dir, exist_ok=True)
        
        # App data directory path
        app_data_dir = f'/data/data/{package}'
        
        results = {
            'package': package,
            'timestamp': timestamp,
            'output_path': output_dir,
            'app_data_dir': app_data_dir,
            'root_access': is_rooted,
            'extracted': {},
            'errors': []
        }
        
        if not is_rooted:
            results['errors'].append("WARNING: Root access not detected. Extraction may fail for protected directories.")
        
        # Extract databases from the app
        if options.get('databases'):
            update_progress("Extracting databases...")
            results['extracted']['databases'] = self.extract_app_databases(device, package, output_dir)
        
        # Extract shared preferences
        if options.get('shared_prefs'):
            update_progress("Extracting shared preferences...")
            results['extracted']['shared_prefs'] = self.extract_shared_preferences(device, package, output_dir)
            
        # Extract cache files
        if options.get('cache'):
            update_progress("Extracting cache files...")
            results['extracted']['cache'] = self.extract_cache(device, package, output_dir)
            
        # Extract internal storage/files
        if options.get('internal_storage') or options.get('media'):
            update_progress("Extracting app files...")
            results['extracted']['files'] = self.extract_app_files(device, package, output_dir)
            
        # Extract app-specific logs
        if options.get('logs'):
            update_progress("Extracting logs...")
            results['extracted']['logs'] = self.extract_app_logs(device, package, output_dir)
        
        # Get app info (doesn't require root)
        update_progress("Getting app info...")
        results['extracted']['app_info'] = self.get_app_info(device, package, output_dir)
        
        update_progress("Saving extraction report...")
            
        # Save extraction report
        report_path = os.path.join(output_dir, 'extraction_report.json')
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
            
        return results
    
    def _pull_with_root(self, device, remote_path, local_path):
        """Pull a file using root access - copies to /sdcard/ first then pulls"""
        import random
        temp_name = f'aktis_{random.randint(10000,99999)}'
        temp_path = f'/sdcard/{temp_name}'
        
        try:
            # Clean up any existing temp file first
            self.adb.shell_command(device, f'rm -f {temp_path}')
            
            # Method 1: Try direct copy if running as root (adb root mode)
            self.adb.shell_command(device, f'cp "{remote_path}" "{temp_path}"')
            check1, _ = self.adb.shell_command(device, f'ls {temp_path} 2>/dev/null')
            
            if not check1 or temp_name not in check1:
                # Method 2: Use su -c with simple syntax
                self.adb.shell_command(device, f'su -c cp "{remote_path}" "{temp_path}"')
                check2, _ = self.adb.shell_command(device, f'ls {temp_path} 2>/dev/null')
                
                if not check2 or temp_name not in check2:
                    # Method 3: Use su 0 
                    self.adb.shell_command(device, f'su 0 cp "{remote_path}" "{temp_path}"')
                    check3, _ = self.adb.shell_command(device, f'ls {temp_path} 2>/dev/null')
                    
                    if not check3 or temp_name not in check3:
                        return False
            
            # Make temp file readable
            self.adb.shell_command(device, f'chmod 644 {temp_path}')
            
            # Pull from temp location
            pull_success = self.adb.pull_file(device, temp_path, local_path)
            
            # Cleanup temp file
            self.adb.shell_command(device, f'rm -f {temp_path}')
            
            return pull_success and os.path.exists(local_path) and os.path.getsize(local_path) > 0
        except Exception as e:
            try:
                self.adb.shell_command(device, f'rm -f {temp_path}')
            except:
                pass
            return False
    
    def _list_files_with_root(self, device, remote_dir, pattern="*"):
        """List files in a directory using root access"""
        files = []
        
        # Build find command
        if pattern == "*":
            find_cmd = f'find "{remote_dir}" -type f 2>/dev/null'
        else:
            find_cmd = f'find "{remote_dir}" -type f -name "{pattern}" 2>/dev/null'
        
        # Try different methods
        # Method 1: Direct (if running as adb root)
        output, _ = self.adb.shell_command(device, find_cmd)
        
        # Method 2: With su -c
        if not output or 'Permission denied' in output:
            output, _ = self.adb.shell_command(device, f'su -c {find_cmd}')
        
        # Method 3: With su 0
        if not output or 'Permission denied' in output:
            output, _ = self.adb.shell_command(device, f'su 0 {find_cmd}')
        
        if output:
            for line in output.split('\n'):
                line = line.strip()
                # Filter valid file paths
                if (line and 
                    line.startswith('/') and
                    'Permission denied' not in line and
                    'No such file' not in line and
                    'find:' not in line):
                    files.append(line)
        
        return files
    
    def diagnose_app_directory(self, device, package):
        """Diagnose what's in the app directory - for debugging"""
        results = {
            'package': package,
            'app_dir': f'/data/data/{package}',
            'exists': False,
            'contents': [],
            'errors': [],
            'su_works': False,
            'adb_root': False
        }
        
        app_dir = f'/data/data/{package}'
        
        # Check if running as adb root
        id_output, _ = self.adb.shell_command(device, 'id')
        if id_output and 'uid=0' in id_output:
            results['adb_root'] = True
        
        # Check if su works
        su_test, _ = self.adb.shell_command(device, 'su -c id')
        if su_test and 'uid=0' in su_test:
            results['su_works'] = True
        else:
            su_test2, _ = self.adb.shell_command(device, 'su 0 id')
            if su_test2 and 'uid=0' in su_test2:
                results['su_works'] = True
        
        # Try to list app directory
        # Method 1: Direct (if adb root)
        output, _ = self.adb.shell_command(device, f'ls -la {app_dir}')
        
        if not output or 'Permission denied' in output:
            # Method 2: su -c
            output, _ = self.adb.shell_command(device, f'su -c ls -la {app_dir}')
        
        if not output or 'Permission denied' in output:
            # Method 3: su 0
            output, _ = self.adb.shell_command(device, f'su 0 ls -la {app_dir}')
        
        if output and 'No such file' not in output and 'Permission denied' not in output:
            results['exists'] = True
            results['contents'] = [l for l in output.split('\n') if l.strip()]
        elif output:
            results['errors'].append(output)
        
        return results
    
    def extract_app_databases(self, device, package, output_dir):
        """Extract all databases from the app's data directory"""
        db_dir = os.path.join(output_dir, 'databases')
        os.makedirs(db_dir, exist_ok=True)
        
        app_db_path = f'/data/data/{package}/databases'
        extracted_files = []
        
        # List database files using root
        db_files = self._list_files_with_root(device, app_db_path)
        
        for remote_file in db_files:
            filename = os.path.basename(remote_file)
            local_path = os.path.join(db_dir, filename)
            
            if self._pull_with_root(device, remote_file, local_path):
                extracted_files.append({
                    'remote_path': remote_file,
                    'local_path': local_path,
                    'filename': filename,
                    'size': os.path.getsize(local_path) if os.path.exists(local_path) else 0
                })
            
        return extracted_files
    
    def extract_shared_preferences(self, device, package, output_dir):
        """Extract shared preferences XML files from the app"""
        prefs_dir = os.path.join(output_dir, 'shared_prefs')
        os.makedirs(prefs_dir, exist_ok=True)
        
        app_prefs_path = f'/data/data/{package}/shared_prefs'
        extracted_files = []
        
        # List preference files using root
        pref_files = self._list_files_with_root(device, app_prefs_path, "*.xml")
        
        # If no .xml files found, try listing all files
        if not pref_files:
            pref_files = self._list_files_with_root(device, app_prefs_path)
        
        for remote_file in pref_files:
            filename = os.path.basename(remote_file)
            local_path = os.path.join(prefs_dir, filename)
            
            if self._pull_with_root(device, remote_file, local_path):
                extracted_files.append({
                    'remote_path': remote_file,
                    'local_path': local_path,
                    'filename': filename,
                    'size': os.path.getsize(local_path) if os.path.exists(local_path) else 0
                })
            
        return extracted_files
    
    def extract_cache(self, device, package, output_dir):
        """Extract cache files from the app"""
        cache_dir = os.path.join(output_dir, 'cache')
        os.makedirs(cache_dir, exist_ok=True)
        
        app_cache_path = f'/data/data/{package}/cache'
        extracted_files = []
        
        # List cache files (limit count to avoid huge extractions)
        cache_files = self._list_files_with_root(device, app_cache_path)[:50]
        
        for remote_file in cache_files:
            filename = os.path.basename(remote_file)
            # Create unique filename to avoid overwrites
            unique_name = remote_file.replace('/', '_').replace(f'_data_data_{package}_cache_', '')
            if len(unique_name) > 100:
                unique_name = filename
            local_path = os.path.join(cache_dir, unique_name)
            
            if self._pull_with_root(device, remote_file, local_path):
                extracted_files.append({
                    'remote_path': remote_file,
                    'local_path': local_path,
                    'filename': filename,
                    'size': os.path.getsize(local_path) if os.path.exists(local_path) else 0
                })
            
        return extracted_files
    
    def extract_app_files(self, device, package, output_dir):
        """Extract files from the app's internal storage"""
        files_dir = os.path.join(output_dir, 'files')
        os.makedirs(files_dir, exist_ok=True)
        
        extracted_files = []
        
        # Paths to check within the app's data directory
        paths_to_check = [
            f'/data/data/{package}/files',
            f'/data/data/{package}/app_webview',
            f'/data/data/{package}/app_chrome',
            f'/data/data/{package}/app_tabs',
            f'/data/data/{package}/no_backup',
        ]
        
        for app_path in paths_to_check:
            # List files using root (limit to 30 per directory)
            app_files = self._list_files_with_root(device, app_path)[:30]
            
            for remote_file in app_files:
                filename = os.path.basename(remote_file)
                # Create structured path
                rel_path = remote_file.replace(f'/data/data/{package}/', '')
                subdir_name = rel_path.split('/')[0] if '/' in rel_path else 'files'
                local_subdir = os.path.join(files_dir, subdir_name)
                os.makedirs(local_subdir, exist_ok=True)
                local_path = os.path.join(local_subdir, filename)
                
                if self._pull_with_root(device, remote_file, local_path):
                    extracted_files.append({
                        'remote_path': remote_file,
                        'local_path': local_path,
                        'filename': filename,
                        'size': os.path.getsize(local_path) if os.path.exists(local_path) else 0
                    })
                
        return extracted_files
    
    def extract_app_logs(self, device, package, output_dir):
        """Extract logcat logs specific to this app"""
        logs_dir = os.path.join(output_dir, 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        extracted_files = []
        
        # Get logcat filtered by package (this doesn't require root)
        log_file = os.path.join(logs_dir, f'{package}_logcat.txt')
        try:
            output, _ = self.adb.shell_command(device, f'logcat -d | grep -i "{package}"')
            if output and len(output.strip()) > 10:
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write(f"=== Logcat for {package} ===\n")
                    f.write(f"Extracted: {datetime.now()}\n")
                    f.write("=" * 80 + "\n\n")
                    f.write(output)
                extracted_files.append({
                    'local_path': log_file,
                    'filename': f'{package}_logcat.txt',
                    'type': 'logcat',
                    'size': os.path.getsize(log_file)
                })
        except Exception as e:
            pass
        
        # Try to get app's own log files using root
        app_log_paths = [
            f'/data/data/{package}/files/logs',
            f'/data/data/{package}/logs',
        ]
        
        for log_path in app_log_paths:
            log_files = self._list_files_with_root(device, log_path)
            for remote_file in log_files:
                filename = os.path.basename(remote_file)
                local_path = os.path.join(logs_dir, filename)
                if self._pull_with_root(device, remote_file, local_path):
                    extracted_files.append({
                        'remote_path': remote_file,
                        'local_path': local_path,
                        'filename': filename,
                        'type': 'app_log',
                        'size': os.path.getsize(local_path) if os.path.exists(local_path) else 0
                    })
            
        return extracted_files
    
    def get_app_info(self, device, package, output_dir):
        """Get information about the app (doesn't require root)"""
        info = {
            'package': package,
            'extraction_time': datetime.now().isoformat()
        }
        
        try:
            # Get package info using dumpsys (no root needed)
            output, _ = self.adb.shell_command(device, f'dumpsys package {package}')
            if output:
                info_file = os.path.join(output_dir, 'app_info.txt')
                with open(info_file, 'w', encoding='utf-8') as f:
                    f.write(output)
                info['dumpsys_file'] = info_file
                
                # Parse some key info
                for line in output.split('\n'):
                    if 'versionName=' in line:
                        info['version'] = line.split('versionName=')[1].split()[0]
                    elif 'firstInstallTime=' in line:
                        info['installed'] = line.split('firstInstallTime=')[1].strip()
                    elif 'lastUpdateTime=' in line:
                        info['updated'] = line.split('lastUpdateTime=')[1].strip()
        except:
            pass
        
        try:
            # Get permissions
            output, _ = self.adb.shell_command(device, f'dumpsys package {package} | grep permission')
            if output:
                perms_file = os.path.join(output_dir, 'permissions.txt')
                with open(perms_file, 'w', encoding='utf-8') as f:
                    f.write(output)
                info['permissions_file'] = perms_file
        except:
            pass
        
        try:
            # Get data directory size using root
            output, _ = self.adb.shell_command(device, f'su -c "du -sh /data/data/{package}"')
            if output and 'cannot' not in output.lower():
                info['data_size'] = output.strip().split()[0] if output.strip() else 'unknown'
            else:
                info['data_size'] = 'requires root'
        except:
            info['data_size'] = 'unknown'
            
        return info
