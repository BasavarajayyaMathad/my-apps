"""
Streamlit Authentication Module
Handles login/logout and session management for Streamlit
"""

import streamlit as st
import time
from user_manager import UserManager, User, PermissionManager
from oauth_manager import OAuthManager, OAuthConfig
from config import TournamentConfig
from urllib.parse import urlparse, parse_qs


class StreamlitAuthManager:
    """Authentication manager for Streamlit application"""
    
    SESSION_KEY_USER = "authenticated_user"
    SESSION_KEY_TOKEN = "session_token"
    
    @staticmethod
    def init_session_state():
        """Initialize authentication session state"""
        if StreamlitAuthManager.SESSION_KEY_USER not in st.session_state:
            st.session_state[StreamlitAuthManager.SESSION_KEY_USER] = None
        if StreamlitAuthManager.SESSION_KEY_TOKEN not in st.session_state:
            st.session_state[StreamlitAuthManager.SESSION_KEY_TOKEN] = None

    
    @staticmethod
    def get_current_user() -> User:
        """Get currently authenticated user"""
        StreamlitAuthManager.init_session_state()
        return st.session_state.get(StreamlitAuthManager.SESSION_KEY_USER)
    
    @staticmethod
    def get_session_token() -> str:
        """Get current session token"""
        StreamlitAuthManager.init_session_state()
        return st.session_state.get(StreamlitAuthManager.SESSION_KEY_TOKEN)
    
    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated"""
        user = StreamlitAuthManager.get_current_user()
        return user is not None
    
    @staticmethod
    def is_admin() -> bool:
        """Check if current user is admin"""
        user = StreamlitAuthManager.get_current_user()
        return user is not None and user.is_admin()
    
    @staticmethod
    def login_user(user: User, token: str):
        """Login user and store in session"""
        st.session_state[StreamlitAuthManager.SESSION_KEY_USER] = user
        st.session_state[StreamlitAuthManager.SESSION_KEY_TOKEN] = token
    
    @staticmethod
    def logout_user():
        """Logout user and clear session"""
        st.session_state[StreamlitAuthManager.SESSION_KEY_USER] = None
        st.session_state[StreamlitAuthManager.SESSION_KEY_TOKEN] = None
    
    @staticmethod
    def render_login_page():
        """Render login page"""
        st.set_page_config(
            page_title="Welcome to AP Carrom Tournament 2026",
            page_icon="🏆",
            layout="wide",
        )
        
        # Load and encode the carrom board image
        import base64
        import os
        
        image_path = "assets/carrom_board.jpg"
        image_base64 = ""
        
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                image_base64 = base64.b64encode(img_file.read()).decode()
        
        st.markdown("""
        <style>
            body {
                background: linear-gradient(135deg, #8B4513 0%, #D2691E 50%, #8B4513 100%);
                min-height: 100vh;
            }
            .main {
                background: linear-gradient(135deg, #f5e6d3 0%, #e8d4b8 100%);
            }
            .stApp {
                background: linear-gradient(135deg, #f5e6d3 0%, #e8d4b8 100%);
            }
            .welcome-container {
                text-align: center;
                padding: 3rem 2rem;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(139, 69, 19, 0.3);
                margin: 2rem auto;
                max-width: 700px;
            }
            .welcome-title {
                font-size: 3rem;
                font-weight: bold;
                color: #8B4513;
                margin: 1rem 0;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
            }
            .welcome-slogan {
                font-size: 1.5rem;
                color: #D2691E;
                font-style: italic;
                margin: 1.5rem 0;
                font-weight: 500;
            }
            .carrom-image-container {
                text-align: center;
                margin: 2rem 0;
            }
            .carrom-image-container img {
                max-width: 300px;
                height: auto;
                border-radius: 10px;
                box-shadow: 0 10px 30px rgba(139, 69, 19, 0.2);
            }
            .login-section {
                margin-top: 3rem;
                padding-top: 2rem;
                border-top: 2px solid #D2691E;
            }
            .oauth-buttons {
                display: flex;
                flex-direction: column;
                gap: 1rem;
                margin: 2rem 0;
            }
            .oauth-button {
                padding: 0.75rem;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                cursor: pointer;
                text-align: center;
                transition: all 0.3s ease;
                background: linear-gradient(135deg, #8B4513 0%, #D2691E 100%);
                color: white;
            }
            .oauth-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(139, 69, 19, 0.3);
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Display welcome section with image and title
        col1, col2, col3 = st.columns([0.5, 3, 0.5])
        
        with col2:
            if image_base64:
                st.markdown(f"""
                <div class="welcome-container">
                    <div class="carrom-image-container">
                        <img src="data:image/jpeg;base64,{image_base64}" alt="Carrom Board">
                    </div>
                    <div class="welcome-title">
                        Welcome to<br>AP Carrom Tournament 2026
                    </div>
                    <div class="welcome-slogan">
                        "Carrom: More Than a Game, It's a Vibe."
                    </div>
                    <div class="login-section">
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="welcome-container">
                    <div class="welcome-title">
                        Welcome to<br>AP Carrom Tournament 2026
                    </div>
                    <div class="welcome-slogan">
                        "Carrom: More Than a Game, It's a Vibe."
                    </div>
                    <div class="login-section">
                """, unsafe_allow_html=True)
                st.warning("⚠️ Carrom board image not found in assets/carrom_board.jpg")
        
        # Check for OAuth code in URL FIRST - before rendering login buttons
        query_params = st.query_params
        if "code" in query_params:
            code = query_params["code"]
            provider = query_params.get("provider", "google")
            
            st.info(f"Processing authentication... Please wait.")
            
            # Handle OAuth callback
            StreamlitAuthManager._handle_oauth_callback(provider, code)
            
            # If user is now authenticated, clear URL and rerun
            if StreamlitAuthManager.is_authenticated():
                # Clear the query parameters
                st.query_params.clear()
                time.sleep(0.5)  # Small delay to ensure session is set
                st.rerun()
            return
        
        st.markdown("### Login to Your Account")
        
        st.info("ℹ️ **Note:** Your session expires when you refresh the page. Simply click the login button below to continue.")
        
        # OAuth Providers
        available_providers = OAuthManager.get_available_providers()
        
        if available_providers:
            cols = st.columns(len(available_providers))
            
            for idx, provider in enumerate(available_providers):
                with cols[idx]:
                    provider_oauth = OAuthManager.get_provider(provider.lower())
                    if provider_oauth:
                        auth_url = provider_oauth.get_auth_url()
                        # Directly redirect to Google login when button is clicked
                        st.link_button(f"🔑 Login with {provider}", auth_url, use_container_width=True)
        else:
            st.warning("""
            ⚠️ No OAuth providers configured!

            Please set your Google OAuth credentials in .env file:
            ```
            GOOGLE_CLIENT_ID=your_client_id
            GOOGLE_CLIENT_SECRET=your_client_secret
            GOOGLE_REDIRECT_URI=http://localhost:8501
            ```
            
            See GOOGLE_OAUTH_SETUP.md for detailed setup instructions.
            """)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    @staticmethod
    def _handle_oauth_callback(provider: str, code: str):
        """Handle OAuth callback and authenticate user"""
        try:
            user_info = OAuthManager.authenticate_with_oauth(provider, code)
            
            if not user_info:
                st.error(f"❌ Failed to authenticate with {provider}")
                st.stop()
                return
            
            user_manager = UserManager()
            user_email = user_info.get("email")
            
            if not user_email:
                st.error("❌ Could not retrieve email from OAuth provider")
                st.stop()
                return
            
            # Check if user exists
            user = user_manager.get_user(user_email)
            
            if not user:
                # Auto-register new users
                # Check if this is the initial admin email - if so, make them admin
                is_initial_admin = user_email == TournamentConfig.INITIAL_ADMIN_EMAIL
                role = "admin" if is_initial_admin else "viewer"
                
                user = user_manager.register_user(
                    email=user_email,
                    name=user_info.get("name", ""),
                    provider=user_info.get("provider", provider),
                    provider_id=user_info.get("provider_id", ""),
                    role=role
                )
                
                if is_initial_admin:
                    st.success(f"✅ Welcome Admin {user.name}!")
                else:
                    st.success(f"✅ Welcome {user.name}! You have been registered as a Viewer.")
            else:
                # User exists - show their role
                role_display = "🔐 Admin" if user.is_admin() else "👁️ Viewer"
                st.success(f"✅ Welcome back {user.name}! ({role_display})")
            
            # Create session
            if user:
                user_manager.log_action(user_email, f"Logged in via {provider}")
                StreamlitAuthManager.login_user(user, "")  # No token needed with JSON
                
                # Clear URL params
                st.query_params.clear()
                
                st.success("🎉 Login successful!")
                st.balloons()
                time.sleep(1)
                st.rerun()
        
        except Exception as e:
            st.error(f"❌ Authentication error: {str(e)}")
            print(f"OAuth callback error: {e}")
            import traceback
            traceback.print_exc()
    
    @staticmethod
    def render_logout_button():
        """Render logout button in sidebar"""
        if StreamlitAuthManager.is_authenticated():
            user = StreamlitAuthManager.get_current_user()
            
            st.sidebar.markdown("---")
            st.sidebar.markdown(f"**👤 Logged in as:** {user.name}")
            st.sidebar.markdown(f"**Role:** {'🔐 Admin' if user.is_admin() else '👁️ Viewer'}")
            
            if st.sidebar.button("🚪 Logout", use_container_width=True):
                StreamlitAuthManager.logout_user()
                st.rerun()
    
    @staticmethod
    def require_authentication(page_func):
        """Decorator to require authentication for a page"""
        def wrapper(*args, **kwargs):
            if not StreamlitAuthManager.is_authenticated():
                st.error("❌ Please login first")
                st.stop()
            return page_func(*args, **kwargs)
        return wrapper
    
    @staticmethod
    def require_admin(page_func):
        """Decorator to require admin role for a page"""
        def wrapper(*args, **kwargs):
            if not StreamlitAuthManager.is_authenticated():
                st.error("❌ Please login first")
                st.stop()
            
            if not StreamlitAuthManager.is_admin():
                st.error("❌ Admin access required")
                st.stop()
            
            return page_func(*args, **kwargs)
        return wrapper


class PermissionChecker:
    """Helper class for checking permissions in Streamlit"""
    
    @staticmethod
    def check_edit_tournament():
        """Check if user can edit tournament"""
        user = StreamlitAuthManager.get_current_user()
        return PermissionManager.can_edit_tournament(user)
    
    @staticmethod
    def check_view_scores():
        """Check if user can view scores"""
        user = StreamlitAuthManager.get_current_user()
        return PermissionManager.can_view_scores(user)
    
    @staticmethod
    def check_update_match():
        """Check if user can update match scores"""
        user = StreamlitAuthManager.get_current_user()
        return PermissionManager.can_update_match(user)
    
    @staticmethod
    def check_manage_users():
        """Check if user can manage users"""
        user = StreamlitAuthManager.get_current_user()
        return PermissionManager.can_manage_users(user)
    
    @staticmethod
    def check_view_audit_log():
        """Check if user can view audit log"""
        user = StreamlitAuthManager.get_current_user()
        return PermissionManager.can_view_audit_log(user)
    
    @staticmethod
    def show_permission_denied():
        """Show permission denied message"""
        st.error("❌ You don't have permission to perform this action")
    
    @staticmethod
    def show_feature_locked_for_viewers():
        """Show message that feature is locked for viewers"""
        st.warning("🔒 This feature is available only for Admins")
