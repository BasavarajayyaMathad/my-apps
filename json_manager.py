"""
JSON File Manager for User Management
Handles JSON file operations for users and audit logs
"""

import json
import os
from typing import Optional, List, Dict
from datetime import datetime


class JSONFileManager:
    """JSON file manager for user and audit data"""
    
    USERS_FILE = "users.json"
    AUDIT_LOG_FILE = "audit_log.json"
    
    # Default users structure
    DEFAULT_USERS_STRUCTURE = {
        "Users": []
    }
    
    DEFAULT_AUDIT_STRUCTURE = {
        "AuditLog": []
    }
    
    def __init__(self):
        """Initialize JSON file manager and create files if needed"""
        self.users_file = self.USERS_FILE
        self.audit_file = self.AUDIT_LOG_FILE
        self.init_files()
    
    def init_files(self):
        """Initialize JSON files if they don't exist"""
        # Initialize users.json
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump(self.DEFAULT_USERS_STRUCTURE, f, indent=2)
        
        # Initialize audit_log.json
        if not os.path.exists(self.audit_file):
            with open(self.audit_file, 'w') as f:
                json.dump(self.DEFAULT_AUDIT_STRUCTURE, f, indent=2)
    
    def load_users(self) -> List[Dict]:
        """Load all users from JSON file"""
        try:
            with open(self.users_file, 'r') as f:
                data = json.load(f)
                return data.get('Users', [])
        except Exception as e:
            print(f"Error loading users: {e}")
            return []
    
    def save_users(self, users: List[Dict]) -> bool:
        """Save users to JSON file"""
        try:
            data = {'Users': users}
            with open(self.users_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving users: {e}")
            return False
    
    def get_user(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        users = self.load_users()
        for user in users:
            if user.get('Name') == email:
                return user
        return None
    
    def add_user(self, email: str, name: str, provider: str, role: str = 'viewer') -> bool:
        """Add a new user to JSON file"""
        users = self.load_users()
        
        # Check if user already exists
        if any(u.get('Name') == email for u in users):
            return False
        
        # Add new user
        new_user = {
            "Name": email,
            "Role": role,
            "DisplayName": name,
            "Provider": provider,
            "CreatedAt": datetime.now().isoformat(),
            "LastLogin": datetime.now().isoformat()
        }
        
        users.append(new_user)
        success = self.save_users(users)
        
        if success:
            self.log_action(email, f"User registered via {provider}")
        
        return success
    
    def update_user_role(self, email: str, role: str) -> bool:
        """Update user role"""
        users = self.load_users()
        
        for user in users:
            if user.get('Name') == email:
                user['Role'] = role
                return self.save_users(users)
        
        return False
    
    def update_user_last_login(self, email: str) -> bool:
        """Update user's last login timestamp"""
        users = self.load_users()
        
        for user in users:
            if user.get('Name') == email:
                user['LastLogin'] = datetime.now().isoformat()
                return self.save_users(users)
        
        return False
    
    def disable_user(self, email: str) -> bool:
        """Disable user by removing from list"""
        users = self.load_users()
        users = [u for u in users if u.get('Name') != email]
        return self.save_users(users)
    
    def list_all_users(self) -> List[Dict]:
        """Get all users"""
        return self.load_users()
    
    def get_user_count(self) -> int:
        """Get total user count"""
        return len(self.load_users())
    
    def log_action(self, user_email: Optional[str], action: str, details: str = None) -> bool:
        """Log user action to audit log"""
        try:
            with open(self.audit_file, 'r') as f:
                data = json.load(f)
            
            log_entry = {
                "User": user_email or "System",
                "Action": action,
                "Details": details or "",
                "Timestamp": datetime.now().isoformat()
            }
            
            data['AuditLog'].append(log_entry)
            
            # Keep only last 500 audit entries to avoid huge file
            if len(data['AuditLog']) > 500:
                data['AuditLog'] = data['AuditLog'][-500:]
            
            with open(self.audit_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error logging action: {e}")
            return False
    
    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """Get audit log entries"""
        try:
            with open(self.audit_file, 'r') as f:
                data = json.load(f)
            
            log_entries = data.get('AuditLog', [])
            # Return last 'limit' entries in reverse order (newest first)
            return log_entries[-limit:][::-1]
        except Exception as e:
            print(f"Error reading audit log: {e}")
            return []
    
    def export_audit_log_csv(self) -> str:
        """Export audit log as CSV string"""
        import csv
        from io import StringIO
        
        log_entries = self.get_audit_log(limit=1000)
        
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=['User', 'Action', 'Details', 'Timestamp'])
        writer.writeheader()
        
        for entry in reversed(log_entries):  # Reverse to show newest first
            writer.writerow(entry)
        
        return output.getvalue()
