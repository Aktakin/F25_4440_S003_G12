"""
Data Extractor Module (Andriller-like)
Extracts various types of data from Android apps
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
        
    def extract_app_data(self, device, package, options, output_base_dir):
        """Extract data from an app"""
        from modules.adb_connector import ADBConnector
        
        # Get ADB connector if not set
        if not self.adb:
            self.adb = ADBConnector()
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(output_base_dir, package, timestamp)
        os.makedirs(output_dir, exist_ok=True)
        
        results = {
            'package': package,
            'timestamp': timestamp,
            'output_path': output_dir,
            'extracted': {}
        }
        
        # Extract messages (SMS/MMS)
        if options.get('messages'):
            results['extracted']['messages'] = self.extract_messages(device, package, output_dir)
            
        # Extract contacts
        if options.get('contacts'):
            results['extracted']['contacts'] = self.extract_contacts(device, package, output_dir)
            
        # Extract call logs
        if options.get('calls'):
            results['extracted']['call_logs'] = self.extract_call_logs(device, package, output_dir)
            
        # Extract media files
        if options.get('media'):
            results['extracted']['media'] = self.extract_media(device, package, output_dir)
            
        # Extract databases
        if options.get('databases'):
            results['extracted']['databases'] = self.extract_databases(device, package, output_dir)
            
        # Extract logs
        if options.get('logs'):
            results['extracted']['logs'] = self.extract_logs(device, package, output_dir)
            
        # Save extraction report
        report_path = os.path.join(output_dir, 'extraction_report.json')
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)
            
        return results
        
    def extract_messages(self, device, package, output_dir):
        """Extract SMS/MMS messages"""
        messages_dir = os.path.join(output_dir, 'messages')
        os.makedirs(messages_dir, exist_ok=True)
        
        # Try to extract from common SMS database locations
        sms_paths = [
            '/data/data/com.android.providers.telephony/databases/mmssms.db',
            '/data/data/com.android.mms/databases/',
        ]
        
        extracted_files = []
        for path in sms_paths:
            try:
                local_path = os.path.join(messages_dir, os.path.basename(path))
                if self.adb.pull_file(device, path, local_path):
                    extracted_files.append(local_path)
            except:
                pass
                
        return extracted_files
        
    def extract_contacts(self, device, package, output_dir):
        """Extract contacts"""
        contacts_dir = os.path.join(output_dir, 'contacts')
        os.makedirs(contacts_dir, exist_ok=True)
        
        contacts_path = '/data/data/com.android.providers.contacts/databases/contacts2.db'
        extracted_files = []
        
        try:
            local_path = os.path.join(contacts_dir, 'contacts2.db')
            if self.adb.pull_file(device, contacts_path, local_path):
                extracted_files.append(local_path)
        except:
            pass
            
        return extracted_files
        
    def extract_call_logs(self, device, package, output_dir):
        """Extract call logs"""
        calls_dir = os.path.join(output_dir, 'call_logs')
        os.makedirs(calls_dir, exist_ok=True)
        
        call_log_path = '/data/data/com.android.providers.contacts/databases/calllog.db'
        extracted_files = []
        
        try:
            local_path = os.path.join(calls_dir, 'calllog.db')
            if self.adb.pull_file(device, call_log_path, local_path):
                extracted_files.append(local_path)
        except:
            pass
            
        return extracted_files
        
    def extract_media(self, device, package, output_dir):
        """Extract media files from app"""
        media_dir = os.path.join(output_dir, 'media')
        os.makedirs(media_dir, exist_ok=True)
        
        # Try to find app's media directories
        app_data_dir = f'/data/data/{package}'
        media_paths = [
            f'{app_data_dir}/files/',
            f'{app_data_dir}/cache/',
            f'{app_data_dir}/media/',
        ]
        
        extracted_files = []
        for path in media_paths:
            try:
                # List files in directory
                output, _ = self.adb.shell_command(device, f'find {path} -type f 2>/dev/null')
                if output:
                    for line in output.split('\n'):
                        if line.strip():
                            filename = os.path.basename(line)
                            local_path = os.path.join(media_dir, filename)
                            if self.adb.pull_file(device, line, local_path):
                                extracted_files.append(local_path)
            except:
                pass
                
        return extracted_files
        
    def extract_databases(self, device, package, output_dir):
        """Extract app databases"""
        db_dir = os.path.join(output_dir, 'databases')
        os.makedirs(db_dir, exist_ok=True)
        
        app_data_dir = f'/data/data/{package}'
        db_path = f'{app_data_dir}/databases/'
        
        extracted_files = []
        try:
            # List all databases
            output, _ = self.adb.shell_command(device, f'find {db_path} -name "*.db" 2>/dev/null')
            if output:
                for line in output.split('\n'):
                    if line.strip():
                        filename = os.path.basename(line)
                        local_path = os.path.join(db_dir, filename)
                        if self.adb.pull_file(device, line, local_path):
                            extracted_files.append(local_path)
        except:
            pass
            
        return extracted_files
        
    def extract_logs(self, device, package, output_dir):
        """Extract logcat logs"""
        logs_dir = os.path.join(output_dir, 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        log_file = os.path.join(logs_dir, 'logcat.txt')
        try:
            # Get logcat for specific package
            output, _ = self.adb.shell_command(device, f'logcat -d | grep {package}')
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(output)
            return [log_file]
        except:
            return []

