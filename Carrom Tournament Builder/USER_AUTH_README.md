# Carrom Tournament Builder - With User Management

A comprehensive Streamlit application for managing carrom tournaments with advanced features including user authentication, role-based access control, and detailed audit logging.

## New Features: User Management & Authentication

### User Roles

The application now supports two user roles:

1. **Admin** 🔐
   - Full access to all features
   - Can create and manage tournaments
   - Can update match scores
   - Can reset tournaments
   - User management capabilities
   - Can view audit logs

2. **Viewer** 👁️
   - Read-only access
   - Can view group standings
   - Can view match schedules and results
   - Cannot edit or update any data

### Authentication Methods

Users can login using their email with the following OAuth providers:
- **Google OAuth**
- **Microsoft Azure AD**
- **Yahoo Email**

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure OAuth Providers

#### Google OAuth Setup:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Google+ API
4. Create OAuth 2.0 credentials (Web Application)
5. Add authorized redirect URI: `http://localhost:8501`
6. Copy Client ID and Client Secret

#### Microsoft OAuth Setup:
1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to App registrations
3. Create a new application
4. Add Web platform redirect URI: `http://localhost:8501`
5. Create a client secret
6. Copy Application ID and Secret

#### Yahoo OAuth Setup:
1. Go to [Yahoo Developer Network](https://developer.yahoo.com/)
2. Create a new application
3. Add callback URI: `http://localhost:8501`
4. Copy Client ID and Secret

### 3. Create .env File

Copy `.env.example` to `.env` and fill in your OAuth credentials:

```env
# OpenAI API Key (optional, for NLP features)
OPENAI_API_KEY=your_key_here

# Tournament Settings
MATCH_DURATION_MINUTES=20
POINTS_PER_WIN=2
NUMBER_OF_GROUPS=2

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8501

# Microsoft OAuth
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret
MICROSOFT_REDIRECT_URI=http://localhost:8501

# Yahoo OAuth
YAHOO_CLIENT_ID=your_yahoo_client_id
YAHOO_CLIENT_SECRET=your_yahoo_client_secret
YAHOO_REDIRECT_URI=http://localhost:8501

# Set your admin email (will be promoted to admin on first login)
INITIAL_ADMIN_EMAIL=your_email@gmail.com
```

## Running the Application

### Local Development

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

### Production Deployment

For production, update the redirect URIs to your domain:
```env
GOOGLE_REDIRECT_URI=https://your-domain.com
MICROSOFT_REDIRECT_URI=https://your-domain.com
YAHOO_REDIRECT_URI=https://your-domain.com
```

## Database

The application uses SQLite for data persistence:
- `tournament_users.db` - User authentication and audit logs
- `tournament_results.xlsx` - Tournament data (teams, matches, standings)

## File Structure

```
├── app.py                    # Main Streamlit application
├── config.py                # Configuration settings
├── tournament_engine.py      # Tournament logic
├── models.py                # Data models
├── nlp_processor.py         # NLP integration (OpenAI)
├── visualizations.py        # Chart generation
├── db_manager.py            # Database operations
├── user_manager.py          # User management logic
├── oauth_manager.py         # OAuth integration
├── streamlit_auth.py        # Streamlit authentication
├── requirements.txt         # Python dependencies
├── .env.example              # Environment variables template
└── README.md                # This file
```

## Usage Guide

### First Time Setup

1. **Login with Email**
   - Click on one of the OAuth provider buttons (Google, Microsoft, or Yahoo)
   - Use your email to authenticate
   - The first user with the `INITIAL_ADMIN_EMAIL` will be promoted to Admin

2. **Admin Creates Tournament**
   - Upload teams Excel file
   - Configure tournament settings
   - Initialize tournament
   - Start managing matches

3. **Other Users Join**
   - Users login with their email
   - Viewers can see standings and match results
   - Only Admins can update match scores

### Admin Features

#### User Management (Admin Panel)
- View all registered users
- Change user roles (Promote/Demote)
- Disable user accounts
- View complete audit log

#### Tournament Management
- Create and initialize tournaments
- Update match scores
- Reset tournament (with confirmation)
- Save tournament data

### Viewer Features
- View group standings
- View match schedules
- View analytics and statistics
- View match results (read-only)

## Security Features

- **Role-Based Access Control (RBAC)**: Different permission levels for admin and viewer roles
- **OAuth 2.0 Authentication**: Secure email-based authentication
- **Session Management**: Automatic session timeouts after 30 days
- **Audit Logging**: Complete audit trail of all admin actions
- **Permission Checks**: All write operations require admin role

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    provider TEXT NOT NULL,  -- google, microsoft, yahoo
    provider_id TEXT,
    role TEXT DEFAULT 'viewer',  -- admin, viewer
    created_at TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
)
```

### Sessions Table
```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
)
```

### Audit Log Table
```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    action TEXT NOT NULL,
    details TEXT,
    created_at TIMESTAMP
)
```

## Features

### Tournament Management
- ✅ Create tournaments with customizable settings
- ✅ Divide teams into groups (2 or 4 groups)
- ✅ Round-robin group stage
- ✅ Automatic knockout bracket generation
- ✅ Match scheduling
- ✅ Score tracking and winner determination
- ✅ Standings and rankings
- ✅ Analytics and statistics

### Authentication & Authorization
- ✅ OAuth 2.0 email-based login
- ✅ Role-based access control (Admin/Viewer)
- ✅ Session management
- ✅ Audit logging
- ✅ User management interface

### User Interface
- ✅ Responsive design
- ✅ Real-time updates
- ✅ Data export (CSV)
- ✅ Tournament bracket visualization
- ✅ Statistical charts and graphs

## Troubleshooting

### OAuth Login Issues

**Problem**: "Failed to authenticate with [Provider]"
- **Solution**: Check that OAuth credentials are correctly set in `.env`
- Check redirect URIs match between .env and OAuth provider settings
- Ensure at least one provider is configured

### Database Issues

**Problem**: "tournament_users.db is locked"
- **Solution**: The application is using the database. Wait for other sessions to close or delete the file to reset.

**Problem**: Users not appearing after registration
- **Solution**: Clear browser cache and cookies, then login again

### Permission Issues

**Problem**: "Admin access required" message
- **Solution**: Your account needs to be promoted to admin. Ask an existing admin to change your role via the Admin Panel.

## Support

For issues or questions:
1. Check the audit log for error details
2. Review OAuth provider settings
3. Clear browser cache and try again
4. Reset the database: `rm tournament_users.db`

## License

This project is licensed under the MIT License.

## Version History

### v2.0.0 (Current)
- Added user authentication with OAuth
- Implemented role-based access control
- Added audit logging
- User management interface
- Admin panel

### v1.0.0
- Initial tournament management features
- NLP command processing
- Tournament analytics
