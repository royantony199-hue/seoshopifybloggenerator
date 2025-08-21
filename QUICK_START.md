# 🚀 Quick Start Guide - SEO Blog Automation SaaS

## Start the Application

### 1. Backend Server
```bash
cd /Users/royantony/blue-lotus-seo/saas-platform/backend
python3 -m uvicorn app.main:app --reload --port 8000
```
**Status**: Should show "✅ SEO server running correctly"

### 2. Frontend Server
```bash
cd /Users/royantony/blue-lotus-seo/saas-platform/frontend  
npm run dev
```
**Access**: http://localhost:3001

## Test the Manual Keyword Feature

### Step 1: Register/Login
- Go to http://localhost:3001/register
- Create account: email + password + names + tenant name
- Login automatically redirects to dashboard

### Step 2: Add Keywords Manually
1. Click "Add Keywords" from dashboard OR go to "Keywords" page
2. Click "Upload Keywords" tab
3. Select "Enter Manually" radio button
4. Enter test keywords:
   ```
   CBD oil for pain
   best CBD gummies, 15000, Health, 35
   CBD for sleep, 12000, Sleep, 40
   organic hemp products
   ```
5. Click "Process Keywords" → Should show "Successfully processed 4 keywords!"
6. Review preview table
7. Fill in Campaign Name (e.g., "Test Campaign")
8. Click "Upload to Server"

### Step 3: View Keywords
1. Click "Manage Keywords" tab
2. Should see your manually entered keywords with:
   - Status: Ready/Pending  
   - Search volumes (where provided)
   - Categories (Health, Sleep, General)
   - Generate Blog buttons

### Step 4: Test Dashboard Navigation
1. Go back to Dashboard
2. All 4 cards should have working navigation:
   - "Connect Store" → Settings page
   - "Add Keywords" → Keywords page  
   - "Generate Blogs" → Keywords page
   - "View Blogs" → Blogs page

## Current Features Verified Working ✅

- [x] Authentication system (register/login/logout)
- [x] Manual keyword input with preview
- [x] File upload keyword import
- [x] Dashboard quick-start guide  
- [x] Keywords management and sorting
- [x] Loading states and error handling
- [x] User menu with logout option
- [x] Environment variables configured

## API Endpoints Working

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login  
- `GET /api/keywords/` - Get keywords list
- `POST /api/keywords/upload` - Upload keywords (file/manual)
- `GET /api/keywords/stats` - Keyword statistics
- `GET /health` - Health check

## File Locations

**Backend**: `/Users/royantony/blue-lotus-seo/saas-platform/backend/`  
**Frontend**: `/Users/royantony/blue-lotus-seo/saas-platform/frontend/`  
**Database**: `backend/seo_saas.db`

## Troubleshooting

**Backend won't start**: Check if port 8000 is free
**Frontend errors**: Ensure backend is running first  
**Manual keywords not showing**: Check browser network tab for API errors

---
**Last Updated**: August 22, 2025  
**Version**: MVP v1.0 with Manual Keyword Input