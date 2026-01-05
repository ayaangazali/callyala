# 🚀 Deploying to Vercel - Complete Guide

## Problem Fixed
The build was failing because Vercel was trying to run `vite` from the root directory, but your frontend is in a subfolder.

## ✅ What I Fixed

### 1. Created `vercel.json` Configuration
```json
{
  "version": 2,
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist",
  "installCommand": "npm install --prefix frontend",
  "framework": null,
  "devCommand": "cd frontend && npm run dev"
}
```

### 2. Updated Root `package.json`
Changed the build script to install dependencies first:
```json
"build": "npm install --prefix frontend && cd frontend && npm run build"
```

---

## 📋 Deploy to Vercel - Step by Step

### Option 1: Via Vercel Dashboard (Recommended)

1. **Go to Vercel Dashboard**
   - Visit: https://vercel.com/new
   - Connect your GitHub account if not already

2. **Import Your Repository**
   - Click "Add New Project"
   - Select "Import Git Repository"
   - Choose `callyala` repository

3. **Configure Project Settings**
   
   **Framework Preset**: Other (or leave blank)
   
   **Root Directory**: `./` (leave as root)
   
   **Build Command**:
   ```bash
   cd frontend && npm install && npm run build
   ```
   
   **Output Directory**:
   ```
   frontend/dist
   ```
   
   **Install Command**:
   ```bash
   npm install --prefix frontend
   ```

4. **Environment Variables** (Important!)
   
   Add these in Vercel dashboard under "Environment Variables":
   
   ```
   VITE_API_URL=https://your-backend-url.com
   ```
   
   If you want to use the backend:
   ```
   VITE_API_URL=https://api.callyala.com
   ```
   
   Or for local development:
   ```
   VITE_API_URL=http://localhost:8000
   ```

5. **Click "Deploy"**
   - Vercel will build and deploy
   - Should take 2-3 minutes
   - You'll get a URL like: `callyala.vercel.app`

---

### Option 2: Via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy from Root Directory**
   ```bash
   cd /Users/ayaangazali/Documents/hackathons/callyala
   vercel
   ```

4. **Follow Prompts**
   - Set up and deploy: Yes
   - Which scope: Your account
   - Link to existing project: No
   - Project name: callyala
   - Directory: `./` (root)
   - Override settings: No (it will use vercel.json)

5. **Deploy to Production**
   ```bash
   vercel --prod
   ```

---

## 🔧 Troubleshooting

### Error: "vite: command not found"
**Cause**: Dependencies not installed in frontend folder  
**Fix**: Already fixed in `vercel.json` with proper install command

### Error: "Cannot find module 'vite'"
**Cause**: Same as above  
**Fix**: Build command now includes `npm install`

### Error: "Output directory not found"
**Cause**: Wrong output directory path  
**Fix**: Set to `frontend/dist` in `vercel.json`

### Build Timeout
**Cause**: Large dependencies  
**Fix**: Vercel gives 15 minutes for builds (should be enough)

---

## 📦 What Gets Deployed

### Frontend Only
- Your React app from `/frontend`
- Built with Vite
- Deployed to Vercel's CDN
- Fast global access

### Backend (Separate Deployment Needed)
Your FastAPI backend at `/backend` needs separate deployment:

**Options**:
1. **Railway**: https://railway.app
2. **Render**: https://render.com
3. **DigitalOcean App Platform**: https://www.digitalocean.com/products/app-platform
4. **Heroku**: https://www.heroku.com
5. **AWS Lambda** (via Mangum): Advanced option

---

## 🌐 Backend Deployment Quick Guide

### Deploy Backend to Railway (Recommended)

1. **Create Account**: https://railway.app
2. **New Project** → Deploy from GitHub
3. **Select** `callyala` repo
4. **Settings**:
   - Root Directory: `/backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   
5. **Environment Variables**:
   ```
   APP_ENV=production
   PORT=8000
   MOCK_MODE=false
   ANTHROPIC_API_KEY=sk-ant-api03-47sq57...
   ELEVENLABS_API_KEY=sk_f24dea7ff1c330421dec...
   ELEVENLABS_AGENT_ID=agent_3501kdgfqxhjfx8bs71qmgb30dgj
   ELEVENLABS_PHONE_NUMBER_ID=phnum_8901kdgfqh0xec1snhwhc7ydyxyj
   ```

6. **Deploy** → Get URL like: `callyala-backend.railway.app`

7. **Update Frontend** in Vercel:
   - Environment Variables
   - `VITE_API_URL=https://callyala-backend.railway.app`
   - Redeploy frontend

---

## 📝 Vercel Project Settings

After first deployment, you can configure:

### General
- **Project Name**: callyala
- **Framework**: Other
- **Root Directory**: `./`
- **Node Version**: 18.x (automatic)

### Build & Development
- **Build Command**: `cd frontend && npm install && npm run build`
- **Output Directory**: `frontend/dist`
- **Install Command**: `npm install --prefix frontend`
- **Development Command**: `cd frontend && npm run dev`

### Environment Variables
```
VITE_API_URL=https://your-backend-url.com
```

### Domains
- Auto: `callyala.vercel.app`
- Custom: Add your own domain

---

## ✅ Testing Deployment

### 1. Check Build Logs
- Go to Vercel dashboard
- Click on your deployment
- Check "Build Logs" tab
- Should see: ✓ built successfully

### 2. Test the Site
- Visit your Vercel URL
- Test language switcher (🌐)
- Check if UI loads properly
- Test features

### 3. Check API Connection
- Open browser console (F12)
- Look for API calls
- If backend not deployed yet, will see errors (expected)

---

## 🎯 Complete Deployment Checklist

- [ ] `vercel.json` created ✅
- [ ] `package.json` build script updated ✅
- [ ] Push changes to GitHub
- [ ] Import project to Vercel
- [ ] Configure build settings
- [ ] Add environment variables
- [ ] Deploy frontend
- [ ] Deploy backend (Railway/Render)
- [ ] Update `VITE_API_URL` in Vercel
- [ ] Test production site
- [ ] Add custom domain (optional)

---

## 🚀 Quick Deploy Commands

```bash
# 1. Commit your changes
git add .
git commit -m "Add Vercel configuration"
git push origin main

# 2. Deploy via CLI (alternative to dashboard)
vercel --prod

# 3. Or just push to GitHub and let Vercel auto-deploy
git push origin main
```

---

## 📊 Expected Build Output

```
✓ 3310 modules transformed.
✓ built in 3.73s

Build completed successfully!
Output directory: frontend/dist
```

---

## 🎉 You're Done!

Your frontend will be live at:
- **Vercel URL**: `https://callyala.vercel.app`
- **Custom Domain**: (if you add one)

Next steps:
1. Deploy backend separately
2. Update API URL in Vercel
3. Test everything works
4. Share your live link! 🎊

---

**Date**: January 5, 2026  
**Files Modified**:
- ✅ `vercel.json` (created)
- ✅ `package.json` (updated build script)
- ✅ Ready to deploy!
