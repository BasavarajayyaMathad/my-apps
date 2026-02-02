"""
OAuth Authentication Module
Handles email-based OAuth login for Google
"""

import os
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()


class OAuthConfig:
    """OAuth configuration for Google"""
    
    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501")
    
    @staticmethod
    def is_google_configured() -> bool:
        """Check if Google OAuth is configured"""
        return bool(OAuthConfig.GOOGLE_CLIENT_ID and OAuthConfig.GOOGLE_CLIENT_SECRET)
    
    @staticmethod
    def get_available_providers() -> list:
        """Get list of configured OAuth providers"""
        providers = []
        if OAuthConfig.is_google_configured():
            providers.append("Google")
        return providers


class OAuthProvider:
    """Base class for OAuth providers"""
    
    def get_auth_url(self) -> str:
        """Get OAuth authorization URL"""
        raise NotImplementedError
    
    def exchange_code_for_token(self, code: str) -> Optional[str]:
        """Exchange authorization code for access token"""
        raise NotImplementedError
    
    def get_user_info(self, access_token: str) -> Optional[Dict]:
        """Get user information from OAuth provider"""
        raise NotImplementedError


class GoogleOAuth(OAuthProvider):
    """Google OAuth implementation"""
    
    AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    SCOPES = ["openid", "email", "profile"]
    
    def __init__(self):
        self.client_id = OAuthConfig.GOOGLE_CLIENT_ID
        self.client_secret = OAuthConfig.GOOGLE_CLIENT_SECRET
        self.redirect_uri = OAuthConfig.GOOGLE_REDIRECT_URI
    
    def get_auth_url(self) -> str:
        """Get Google OAuth authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.SCOPES),
            "access_type": "offline",
            "prompt": "consent"
        }
        
        from urllib.parse import urlencode
        return f"{self.AUTHORIZATION_URL}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str) -> Optional[str]:
        """Exchange code for Google access token"""
        try:
            import requests
            
            data = {
                "code": code,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri,
                "grant_type": "authorization_code"
            }
            
            response = requests.post(self.TOKEN_URL, data=data)
            response.raise_for_status()
            
            tokens = response.json()
            return tokens.get("access_token")
        except Exception as e:
            print(f"Error exchanging code for token: {e}")
            return None
    
    def get_user_info(self, access_token: str) -> Optional[Dict]:
        """Get user info from Google"""
        try:
            import requests
            
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(self.USER_INFO_URL, headers=headers)
            response.raise_for_status()
            
            user_info = response.json()
            return {
                "email": user_info.get("email"),
                "name": user_info.get("name", user_info.get("email", "").split("@")[0]),
                "provider": "google",
                "provider_id": user_info.get("id")
            }
        except Exception as e:
            print(f"Error getting user info from Google: {e}")
            return None


class OAuthManager:
    """Manager for OAuth operations"""
    
    @staticmethod
    def get_provider(provider_name: str) -> Optional[OAuthProvider]:
        """Get OAuth provider instance"""
        provider_name = provider_name.lower()
        
        if provider_name == "google" and OAuthConfig.is_google_configured():
            return GoogleOAuth()
        
        return None
    
    @staticmethod
    def get_available_providers() -> list:
        """Get list of available providers"""
        return OAuthConfig.get_available_providers()
    
    @staticmethod
    def authenticate_with_oauth(provider_name: str, code: str) -> Optional[Dict]:
        """Authenticate user with OAuth code"""
        provider = OAuthManager.get_provider(provider_name)
        
        if not provider:
            return None
        
        # Exchange code for token
        access_token = provider.exchange_code_for_token(code)
        
        if not access_token:
            return None
        
        # Get user info
        user_info = provider.get_user_info(access_token)
        
        return user_info
