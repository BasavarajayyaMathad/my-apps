"""
User Management Module
Handles user authentication, registration, and role-based access control
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List
from json_manager import JSONFileManager


class UserRole(Enum):
    """User roles and their permissions"""
    ADMIN = "admin"      # Full access to all features
    VIEWER = "viewer"    # Read-only access to group scores


@dataclass
class User:
    """User data model"""
    id: int
    email: str
    name: str
    provider: str
    role: UserRole
    created_at: str
    last_login: Optional[str] = None
    is_active: bool = True
    
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == UserRole.ADMIN
    
    def is_viewer(self) -> bool:
        """Check if user is viewer"""
        return self.role == UserRole.VIEWER
    
    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "provider": self.provider,
            "role": self.role.value,
            "created_at": self.created_at,
            "last_login": self.last_login,
            "is_active": self.is_active
        }


class UserManager:
    """Manager for user operations"""
    
    def __init__(self):
        """Initialize user manager with JSON file storage"""
        self.json = JSONFileManager()
    
    def register_user(self, email: str, name: str, provider: str, provider_id: str = "", role: str = 'viewer') -> Optional[User]:
        """Register a new user"""
        success = self.json.add_user(email, name, provider, role)
        
        if success:
            user_data = self.json.get_user(email)
            return self._dict_to_user(user_data)
        return None
    
    def get_user(self, email: str) -> Optional[User]:
        """Get user by email"""
        user_data = self.json.get_user(email)
        
        if user_data:
            return self._dict_to_user(user_data)
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID (not applicable for JSON, returns None)"""
        return None
    
    def authenticate_user(self, email: str) -> Optional[User]:
        """Authenticate user (returns user if exists)"""
        user = self.get_user(email)
        
        if user:
            # Update last login
            self.json.update_user_last_login(email)
            return user
        
        return None
    
    def create_session(self, user_id: int) -> str:
        """Create session token for user (not applicable for JSON, returns empty)"""
        return ""
    
    def validate_session(self, token: str) -> Optional[User]:
        """Validate session token (not applicable for JSON, returns None)"""
        return None
    
    def logout_user(self, token: str) -> bool:
        """Logout user (not applicable for JSON, returns True)"""
        return True
    
    def promote_to_admin(self, email: str) -> bool:
        """Promote user to admin (admin only)"""
        return self.json.update_user_role(email, UserRole.ADMIN.value)
    
    def demote_to_viewer(self, email: str) -> bool:
        """Demote user to viewer (admin only)"""
        return self.json.update_user_role(email, UserRole.VIEWER.value)
    
    def get_all_users(self) -> List[User]:
        """Get all users (admin only)"""
        users_data = self.json.list_all_users()
        return [self._dict_to_user(user) for user in users_data]
    
    def disable_user(self, email: str) -> bool:
        """Disable user account (admin only)"""
        return self.json.disable_user(email)
    
    def log_action(self, user_email: Optional[str], action: str, details: str = None) -> bool:
        """Log user action"""
        return self.json.log_action(user_email, action, details)
    
    def get_audit_log(self, limit: int = 100) -> List[dict]:
        """Get audit log (admin only)"""
        return self.json.get_audit_log(limit)
    
    def get_user_count(self) -> int:
        """Get total user count"""
        return self.json.get_user_count()
    
    def _dict_to_user(self, user_dict: dict) -> User:
        """Convert JSON dict to User object"""
        email = user_dict.get('Name', '')
        display_name = user_dict.get('DisplayName', email.split('@')[0])
        
        return User(
            id=hash(email) % 100000,  # Generate a pseudo-ID from email
            email=email,
            name=display_name,
            provider=user_dict.get('Provider', 'unknown'),
            role=UserRole(user_dict.get('Role', 'viewer')),
            created_at=user_dict.get('CreatedAt', ''),
            last_login=user_dict.get('LastLogin'),
            is_active=True  # JSON users are always active
        )


class PermissionManager:
    """Manager for checking user permissions"""
    
    @staticmethod
    def can_edit_tournament(user: Optional[User]) -> bool:
        """Check if user can edit tournament (admin only)"""
        return user is not None and user.is_admin()
    
    @staticmethod
    def can_view_scores(user: Optional[User]) -> bool:
        """Check if user can view scores (all authenticated users)"""
        return user is not None
    
    @staticmethod
    def can_manage_users(user: Optional[User]) -> bool:
        """Check if user can manage users (admin only)"""
        return user is not None and user.is_admin()
    
    @staticmethod
    def can_update_match(user: Optional[User]) -> bool:
        """Check if user can update match scores (admin only)"""
        return user is not None and user.is_admin()
    
    @staticmethod
    def can_view_audit_log(user: Optional[User]) -> bool:
        """Check if user can view audit log (admin only)"""
        return user is not None and user.is_admin()
    
    @staticmethod
    def can_reset_tournament(user: Optional[User]) -> bool:
        """Check if user can reset tournament (admin only)"""
        return user is not None and user.is_admin()
