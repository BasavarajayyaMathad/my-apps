"""
Database Manager for User Management
Handles SQLite database operations for users, roles, and authentication
"""

import sqlite3
import os
from typing import Optional, List, Dict, Tuple
from datetime import datetime
import hashlib
import secrets


class DatabaseManager:
    """SQLite database manager for user and authentication data"""
    
    DB_FILE = "tournament_users.db"
    
    def __init__(self):
        """Initialize database connection and create tables if needed"""
        self.db_file = self.DB_FILE
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    provider_id TEXT,
                    role TEXT DEFAULT 'viewer',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Roles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS roles (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT
                )
            ''')
            
            # Session tokens table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')
            
            # Audit log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')
            
            # Insert default roles if not present
            cursor.execute('''
                INSERT OR IGNORE INTO roles (id, name, description) 
                VALUES (1, 'admin', 'Administrator with full access')
            ''')
            cursor.execute('''
                INSERT OR IGNORE INTO roles (id, name, description) 
                VALUES (2, 'viewer', 'Viewer with read-only access')
            ''')
            
            conn.commit()
        finally:
            conn.close()
    
    def add_user(self, email: str, name: str, provider: str, provider_id: str, role: str = 'viewer') -> Optional[int]:
        """Add a new user to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (email, name, provider, provider_id, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (email, name, provider, provider_id, role))
            
            conn.commit()
            user_id = cursor.lastrowid
            
            # Log action
            self.log_action(user_id, f"User registered via {provider}")
            
            return user_id
        except sqlite3.IntegrityError:
            # User already exists
            return None
        finally:
            conn.close()
    
    def get_user(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM users WHERE email = ? AND is_active = 1', (email,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
        finally:
            conn.close()
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM users WHERE id = ? AND is_active = 1', (user_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
        finally:
            conn.close()
    
    def update_user_role(self, email: str, role: str) -> bool:
        """Update user role (admin only action)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('UPDATE users SET role = ? WHERE email = ?', (role, email))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def list_all_users(self) -> List[Dict]:
        """Get all active users (admin only)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT id, email, name, role, created_at, last_login FROM users WHERE is_active = 1 ORDER BY created_at DESC')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def update_last_login(self, user_id: int) -> bool:
        """Update last login timestamp"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def create_session(self, user_id: int) -> str:
        """Create a new session token"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        token = secrets.token_urlsafe(32)
        
        try:
            cursor.execute('''
                INSERT INTO sessions (user_id, token, expires_at)
                VALUES (?, ?, datetime('now', '+30 days'))
            ''', (user_id, token))
            
            conn.commit()
            return token
        finally:
            conn.close()
    
    def validate_session(self, token: str) -> Optional[int]:
        """Validate session token and return user_id if valid"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT user_id FROM sessions 
                WHERE token = ? AND is_active = 1 AND expires_at > CURRENT_TIMESTAMP
            ''', (token,))
            
            row = cursor.fetchone()
            return row['user_id'] if row else None
        finally:
            conn.close()
    
    def invalidate_session(self, token: str) -> bool:
        """Invalidate a session token"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('UPDATE sessions SET is_active = 0 WHERE token = ?', (token,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def log_action(self, user_id: Optional[int], action: str, details: str = None) -> bool:
        """Log user action for audit trail"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO audit_log (user_id, action, details)
                VALUES (?, ?, ?)
            ''', (user_id, action, details))
            
            conn.commit()
            return True
        finally:
            conn.close()
    
    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """Get audit log (admin only)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT al.id, u.email, al.action, al.details, al.created_at 
                FROM audit_log al
                LEFT JOIN users u ON al.user_id = u.id
                ORDER BY al.created_at DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def disable_user(self, email: str) -> bool:
        """Disable a user account (admin only)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('UPDATE users SET is_active = 0 WHERE email = ?', (email,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def get_user_count(self) -> int:
        """Get total active user count"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) as count FROM users WHERE is_active = 1')
            row = cursor.fetchone()
            return row['count'] if row else 0
        finally:
            conn.close()
    
    def delete_old_sessions(self, days: int = 30) -> int:
        """Delete expired sessions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                DELETE FROM sessions 
                WHERE expires_at < datetime('now', ? || ' days')
            ''', (f'-{days}',))
            
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
    
    def close(self):
        """Close database connection"""
        pass
