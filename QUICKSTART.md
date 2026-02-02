# Quick Start Guide: User Management Setup

## What's New

Your Carrom Tournament Builder now has **complete user authentication and role-based access control**!

### Key Features Added:

✅ **Email-Based OAuth Login** - Users login with Google, Yahoo, or Microsoft accounts
✅ **Two User Roles** - Admins have full control, Viewers have read-only access
✅ **Audit Logging** - All admin actions are tracked
✅ **User Management** - Admins can manage users and roles
✅ **Session Management** - Automatic session tokens with 30-day expiration

---

## Quick Setup (5 minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Choose One OAuth Provider

Pick at least one provider (Google is easiest):

#### Option A: Google OAuth (Recommended)
1. Go to https://console.cloud.google.com/
2. Create a new project
3. Search for "Google+ API" and enable it
4. Click "Create Credentials" → OAuth 2.0 Client ID
5. Application type: Web application
6. Authorized redirect URIs: `http://localhost:8501`
7. Copy Client ID and Secret

#### Option B: Microsoft OAuth
1. Go to https://portal.azure.com/
2. App registrations → New registration
3. Add Web platform with redirect URI: `http://localhost:8501`
4. Certificates & secrets → New client secret
5. Copy Application ID and Secret value

#### Option C: Yahoo OAuth
1. Go to https://developer.yahoo.com/
2. Create application
3. Callback URI: `http://localhost:8501`
4. Copy Client ID and Secret

### Step 3: Create .env File
```bash
# Copy the example
cp .env.example .env

# Edit .env with your OAuth credentials
# Paste your CLIENT_ID and CLIENT_SECRET for at least one provider
```

Example `.env`:
```env
# Paste your OAuth credentials here
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8501

# Set your email as initial admin
INITIAL_ADMIN_EMAIL=your.email@gmail.com

# Optional: OpenAI for NLP features
OPENAI_API_KEY=your_key_here
```

### Step 4: Run the App
```bash
streamlit run app.py
```

---

## First Login

1. Open http://localhost:8501 in your browser
2. Click on your OAuth provider (e.g., "🔑 Google")
3. Authorize the application
4. If this is your `INITIAL_ADMIN_EMAIL`, you'll be promoted to **Admin** automatically
5. Other users will be **Viewers** by default

---

## User Roles Explained

### 👤 Admin Role
- ✅ Create and manage tournaments
- ✅ Update match scores
- ✅ Reset tournaments
- ✅ Manage users (promote/demote/disable)
- ✅ View audit logs
- ✅ Configure tournament settings

### 👁️ Viewer Role
- ✅ View group standings
- ✅ View match schedules and results
- ✅ View tournament analytics
- ❌ Cannot update any data
- ❌ Cannot create tournaments
- ❌ Cannot manage users

---

## Admin Panel

Once logged in as Admin, look for the **⚙️ Admin** tab at the top.

### User Management
- See all registered users
- Change roles (Admin ↔ Viewer)
- Disable user accounts

### Audit Log
- View all admin actions
- Download audit log as CSV
- Track who changed what and when

---

## File Changes Summary

### New Files Created:
- `db_manager.py` - SQLite database operations
- `user_manager.py` - User and permission management
- `oauth_manager.py` - OAuth authentication logic
- `streamlit_auth.py` - Streamlit-specific auth UI
- `USER_AUTH_README.md` - Detailed documentation
- `QUICKSTART.md` - This file

### Modified Files:
- `app.py` - Added login page and permission checks
- `requirements.txt` - Added OAuth and crypto packages
- `config.py` - Added auth configuration
- `.env.example` - OAuth credentials template

### New Database:
- `tournament_users.db` - Created automatically on first run

---

## Common Tasks

### Make Someone an Admin
1. Login as Admin
2. Go to ⚙️ Admin tab
3. Click "User Management"
4. Select user from dropdown
5. Change role to "Admin"
6. Click "Update Role"

### View Who Did What
1. Go to ⚙️ Admin tab
2. Click "Audit Log" tab
3. See all actions with timestamps and users

### Disable a User Account
1. Go to ⚙️ Admin tab
2. Find user in User Management
3. Click "🗑️ Disable User Account"

### Export User Activity
1. Go to ⚙️ Admin tab
2. Click "Audit Log"
3. Click "📥 Download Audit Log (CSV)"

---

## Troubleshooting

### "Failed to authenticate with Google/Microsoft/Yahoo"
1. Check your .env file has correct credentials
2. Verify redirect URI in OAuth provider settings matches .env
3. Make sure at least one provider is configured

### "Only Admins can update match scores"
- Ask an admin to promote your account in the Admin Panel

### "This page is only for Admins"
- You're logged in as Viewer. Contact an admin to change your role.

### Need to Reset Everything
```bash
# Delete the user database to reset
rm tournament_users.db
# Then restart the app and login again
```

---

## Security Notes

- ✅ Passwords are never stored - using OAuth with provider authentication
- ✅ Session tokens expire after 30 days
- ✅ All changes are logged with user and timestamp
- ✅ Only admins can modify data
- ✅ Database uses SQLite for local storage

---

## Next Steps

1. ✅ Complete setup (follow steps above)
2. ✅ First admin logs in
3. ✅ Admin creates a tournament
4. ✅ Other users join and view standings
5. ✅ Admin updates matches and manages users
6. ✅ View audit logs to track activity

---

## Need Help?

1. Check `USER_AUTH_README.md` for detailed docs
2. Review your OAuth provider settings
3. Check `.env` file for correct credentials
4. Look at audit logs to see what's happening
5. Try deleting `tournament_users.db` and starting fresh

---

**Your app is now ready for team collaboration with secure, role-based access!** 🎉
