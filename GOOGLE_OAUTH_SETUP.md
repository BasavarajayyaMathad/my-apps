# Google OAuth Setup Guide

This guide explains how to get your Google OAuth credentials (Client ID and Secret) to enable login functionality in the Carrom Tournament Builder application.

## Step-by-Step Instructions

### 1. Go to Google Cloud Console

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account (create one if needed)

### 2. Create a New Project

1. Click on the **project dropdown** at the top (it shows "My First Project" or similar)
2. Click **NEW PROJECT**
3. Enter a project name: `Carrom Tournament` (or any name you prefer)
4. Click **CREATE**
5. Wait a few seconds for the project to be created, then select it

### 3. Enable Google+ API

1. In the left sidebar, go to **APIs & Services** → **Library**
2. Search for **"Google+ API"** in the search box
3. Click on it and then click **ENABLE**
4. Wait for it to enable (you'll see a blue checkmark)

### 4. Configure OAuth Consent Screen FIRST

⚠️ **IMPORTANT: Do this step first or you won't see the OAuth credentials option!**

1. Go to **APIs & Services** → **OAuth consent screen** (in the left sidebar under "APIs & Services")
2. Select **External** (for testing purposes) and click **CREATE**
3. Fill in the required fields:
   - **App name:** `Carrom Tournament Builder`
   - **User support email:** Your email address
   - Scroll down and fill **Developer contact information:** Your email address
4. Click **SAVE AND CONTINUE**
5. Skip the **Scopes** section - click **SAVE AND CONTINUE** again
6. Skip the **Test users** section - click **SAVE AND CONTINUE** or **BACK TO DASHBOARD**
7. You'll see "Application ready" - your consent screen is now configured ✓

### 5. Create OAuth 2.0 Web Application Credentials

Now that the consent screen is set up, you can create credentials:

1. Go to **APIs & Services** → **Credentials** (in the left sidebar)
2. Click the **+ CREATE CREDENTIALS** button (blue button at the top)
3. A dropdown menu appears - select **OAuth client ID**
4. A dialog box will appear asking **"What type of application are you building?"**
5. **Select "Web application"** from the dropdown
6. Give it a name: `Carrom Tournament App`
7. Under **Authorized redirect URIs**, click **+ ADD URI**
8. Add: `http://localhost:8501`
9. (Optional) If deploying later, add: `https://yourdomain.com`
10. Click **CREATE**

### 7. Copy Your Credentials

A popup will appear with your credentials:
- **Client ID** - Copy this value
- **Client Secret** - Copy this value

Keep these safe! You'll need them in the next step.

### 8. Add Credentials to .env File

1. In your project folder, open or create a `.env` file
2. Add the following lines:
```
GOOGLE_CLIENT_ID=YOUR_CLIENT_ID_HERE
GOOGLE_CLIENT_SECRET=YOUR_CLIENT_SECRET_HERE
GOOGLE_REDIRECT_URI=http://localhost:8501
```

3. Replace `YOUR_CLIENT_ID_HERE` and `YOUR_CLIENT_SECRET_HERE` with the values you copied
4. Save the file

### 9. Test Your Setup

1. Run the application:
```bash
streamlit run app.py
```

2. You should now see a **"🔑 Google"** login button
3. Click it to test the login flow

## Visual Walkthrough - If You're Stuck

### Problem: Don't see "OAuth client ID" option

**Solution:** You need to complete the OAuth Consent Screen first!

1. Look for **"OAuth consent screen"** in the left sidebar (it's between "Library" and "Credentials")
2. If you see a warning message saying "To create an OAuth client ID...", click **CONFIGURE CONSENT SCREEN**
3. Complete that form first, then come back to Credentials

### Problem: See a message "Application NOT public" with yellow warning

This is normal! Just continue. You're setting up a test application, so "External" is correct.

### Step-by-Step Visual Checklist

- [ ] Project created in Google Cloud Console
- [ ] Google+ API is **ENABLED** (check APIs & Services → Library)
- [ ] OAuth consent screen is **CONFIGURED** (check APIs & Services → OAuth consent screen)
- [ ] OAuth credentials are **CREATED** (APIs & Services → Credentials → + CREATE CREDENTIALS → OAuth client ID → Web application)
- [ ] Redirect URI `http://localhost:8501` is **ADDED**
- [ ] Client ID and Secret are **COPIED** to .env file
- [ ] App is **RUNNING** with `streamlit run app.py`

## Troubleshooting

### "Invalid Client ID" Error
- Make sure you've enabled the Google+ API
- Check that your credentials are correctly copied in the .env file
- Ensure no extra spaces or quotes in the .env file

### "Redirect URI mismatch" Error
- Verify that `http://localhost:8501` is added in Google Cloud Console credentials
- Make sure the `GOOGLE_REDIRECT_URI` in .env matches exactly

### OAuth button not appearing
- Check that you have `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in your .env file
- Restart the Streamlit app after adding credentials
- Check the console for error messages

### Login fails silently
- Check the browser console (F12 → Console tab) for errors
- Verify the app is running on `http://localhost:8501`
- Make sure you've accepted any popup windows that appear

## Important Security Notes

⚠️ **Never commit `.env` file to version control!**
- Add `.env` to your `.gitignore` file
- Your Client Secret is sensitive - keep it private
- Only share your Client ID if absolutely necessary

## Deploying to Production

If you want to deploy this app online:

1. Get your actual domain name (e.g., `https://myapp.com`)
2. In Google Cloud Console, add it to **Authorized redirect URIs**:
   - `https://myapp.com`
   - `https://myapp.com/` (with trailing slash)
3. Update `GOOGLE_REDIRECT_URI` in your production `.env` file
4. Deploy your app

## Additional Resources

- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Streamlit Authentication Tutorial](https://docs.streamlit.io/)
- [Google Cloud Console Help](https://cloud.google.com/docs)

## Questions?

If you encounter any issues, check:
1. That all environment variables are correctly set
2. That Google+ API is enabled
3. That redirect URIs are properly configured in Google Cloud Console
4. Browser console for detailed error messages (F12)
