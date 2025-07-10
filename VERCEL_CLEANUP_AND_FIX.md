# Vercel Cleanup and Auth Fix

## 🧹 Step 1: Clean Up Old Deployments
1. **Keep only final-mvp5** (the most recent one)
2. **Delete the others** (final-mvp, final-mvp2, final-mvp3, final-mvp4)

### How to delete old projects:
1. Go to each old project (final-mvp, final-mvp2, etc.)
2. Go to **Settings** → **General** 
3. Scroll down to **"Delete Project"**
4. Delete each old project

## 🔧 Step 2: Fix final-mvp5
After cleaning up, focus on **final-mvp5**:

### Set Environment Variable:
1. Go to **final-mvp5** → **Settings** → **Environment Variables**
2. Add:
   - **Name:** `REACT_APP_API_URL`
   - **Value:** `https://final-mvp-jc3a.onrender.com/api`
   - **Environment:** Production

### Redeploy:
1. Go to **Deployments** tab
2. Click **"Redeploy"** on the latest deployment

## 🎯 Why This Will Fix It
- The frontend will use the correct API URL
- Calls will go to `/api/auth/login` instead of `/auth/login`
- Authentication should work properly

## ✅ Test After Fix
1. Open your app at the final-mvp5 URL
2. Open browser dev tools (F12) → Network tab
3. Try to log in
4. Verify the request goes to `/api/auth/login`

This cleanup approach will eliminate confusion and ensure you're working with just one clean deployment!