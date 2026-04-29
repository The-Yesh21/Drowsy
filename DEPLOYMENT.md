# 🚀 Deployment Guide: Railway.app + Vercel

This guide walks you through deploying the Drowsy Detection System to production using **Railway.app** (backend) and **Vercel** (frontend).

**Estimated Time**: 30-45 minutes  
**Total Cost**: ~$5-10/month (Railway) + Free tier (Vercel)

---

## 📋 Prerequisites

Before starting, ensure you have:

- ✅ GitHub account with the repository pushed
- ✅ Railway account ([sign up here](https://railway.app))
- ✅ Vercel account ([sign up here](https://vercel.com))
- ✅ MongoDB Atlas connection string ready
- ✅ Google Gemini API key ready
- ✅ All environment variables documented

---

## 🚀 Part 1: Deploy Backend on Railway.app

### Step 1: Push Code to GitHub

```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### Step 2: Create Railway Project

1. Go to [Railway.app Dashboard](https://railway.app/dashboard)
2. Click **"Create New Project"**
3. Select **"Deploy from GitHub"**
4. Authorize Railway to access your GitHub account
5. Select your **drowsy-detection** repository
6. Choose the **main** branch

### Step 3: Configure Railway Service

1. Click on the service that was created
2. Go to **Settings** tab
3. Under **Deployment**, set:
   - **Start Command**: `python -m uvicorn main:app --host 0.0.0.0 --port 8000`
   - **Publish Port**: `8000`

### Step 4: Add Environment Variables

1. In Railway dashboard, click on your service
2. Go to **Variables** tab
3. Click **"Add Variable"** and add:

```
MONGODB_URL=mongodb+srv://USERNAME:PASSWORD@cluster.mongodb.net/?appName=Cluster0
DB_NAME=drowsiness_detector
GEMINI_API_KEY=your_google_gemini_api_key
JWT_SECRET=your_super_secret_jwt_key_change_this
JWT_EXPIRE_MINUTES=1440
```

> ⚠️ **Important**: Make sure these are production secrets, not your development ones!

### Step 5: Configure Health Check (Optional but Recommended)

1. Go to **Settings**
2. Set **Health Check URL**: `/`
3. This ensures Railway monitors your service

### Step 6: Deploy

1. Click **"Deploy"** button
2. Wait for the build to complete (2-5 minutes)
3. Once deployed, click **"View Logs"** to verify it's running

**You'll see output like:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 7: Get Your Backend URL

1. In Railway, go to your service
2. Look for **"Domain"** - it will be something like:
   ```
   https://drowsy-api-production.up.railway.app
   ```
3. **Save this URL** - you'll need it for the frontend!

---

## 📱 Part 2: Deploy Frontend on Vercel

### Step 1: Connect Frontend Repo

1. Go to [Vercel.com](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Select the **dashboard** folder as root directory
5. Click **"Deploy"**

### Step 2: Configure Environment Variables

**Before Vercel builds**, set environment variables:

1. After import, you'll see **"Configure Project"** page
2. Under **Environment Variables**, add:

```
VITE_API_URL=https://your-railway-app.up.railway.app
VITE_WS_URL=wss://your-railway-app.up.railway.app
```

3. Click **"Deploy"**

### Step 3: Monitor Deployment

1. Vercel will build and deploy automatically
2. Once complete, you'll see a success message
3. Your frontend URL will be displayed (e.g., `https://drowsy-detection.vercel.app`)

### Step 4: Test the Connection

1. Open your Vercel frontend URL in browser
2. Go to **Settings** or **Console** in browser DevTools
3. Check that API calls are going to your Railway backend
4. Try logging in to verify everything connects

---

## ✅ Verification Checklist

- [ ] Backend is running on Railway.app
- [ ] Frontend is deployed on Vercel
- [ ] Environment variables are set on both platforms
- [ ] MongoDB Atlas connection works
- [ ] Gemini API key is valid
- [ ] Frontend can fetch data from backend
- [ ] WebSocket connection works (check live metrics)
- [ ] Login/registration works
- [ ] Session recording starts successfully

---

## 🔧 Troubleshooting

### Backend won't start on Railway

**Check logs:**
```
Railway Dashboard → Your Service → View Logs
```

**Common issues:**
- ❌ Missing environment variables
- ❌ MongoDB connection string is incorrect
- ❌ Port 8000 is not exposed

**Solution:**
```bash
# Re-add environment variables
# Check MongoDB connection in MongoDB Atlas
# Verify railway.toml is correct
```

### Frontend can't connect to backend

**Check in browser console:**
1. Open DevTools (F12)
2. Go to Network tab
3. Try logging in
4. Look for failed requests

**Common issues:**
- ❌ `VITE_API_URL` not set correctly
- ❌ Backend not running
- ❌ CORS not configured

**Solution:**
```
Vercel → Settings → Environment Variables
Update VITE_API_URL to your Railway domain
```

### WebSocket connection fails

**In browser console, you'll see:**
```
WebSocket connection failed
```

**Solution:**
1. Ensure `VITE_WS_URL` starts with `wss://` (not `ws://`)
2. Check backend logs for WebSocket errors
3. Verify CORS allows WebSocket connections

---

## 📊 Monitoring Your Deployment

### Railway.app Monitoring

1. Dashboard → Your Service → Logs
2. Watch for errors or anomalies
3. Set up alerts (optional)

### Vercel Monitoring

1. Dashboard → Your Project → Analytics
2. View real-time traffic
3. Check build logs

### MongoDB Atlas Monitoring

1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Clusters → Your Cluster → Monitoring
3. View connection stats and performance

---

## 💡 Pro Tips

### Auto-deploy on Push
Both Railway and Vercel automatically deploy when you push to GitHub. Just commit and push!

```bash
git add .
git commit -m "Fix bug"
git push origin main
# ✅ Automatically deploys to both platforms
```

### Scaling Up (Future)
- **Railway**: Upgrade plan when traffic increases
- **Vercel**: Already auto-scales, pay only for usage

### Custom Domain (Optional)
- Railway: Add custom domain in Settings
- Vercel: Add custom domain in Settings → Domains

### Environment-Specific Config
Create `.env.production` for production-only variables (not recommended for secrets)

---

## 🔒 Security Best Practices

### For Production

1. ✅ Use strong JWT secrets (32+ characters)
2. ✅ Rotate secrets regularly
3. ✅ Enable MongoDB IP whitelisting
4. ✅ Use HTTPS everywhere (automatic with Railway + Vercel)
5. ✅ Enable CORS only for your frontend domain
6. ✅ Add rate limiting to APIs
7. ✅ Monitor logs for suspicious activity
8. ✅ Keep dependencies updated

### Secrets Management

```bash
# ❌ NEVER commit .env files
# ✅ ALWAYS use platform environment variables

# Before pushing:
git rm --cached .env
echo ".env" >> .gitignore
git commit -m "Remove .env from tracking"
```

---

## 📈 Next Steps

### 1. Set Up Custom Domain (Optional)
- Railway: Settings → Custom Domains
- Vercel: Settings → Domains

### 2. Enable SSL/TLS (Automatic)
- Already enabled on both platforms

### 3. Set Up Backups
- MongoDB Atlas: Backup → Enable Automated Backups
- Railway: Currently handled automatically

### 4. Monitor Performance
- Set up alerting for both platforms
- Configure log aggregation
- Track error rates

### 5. Plan Scaling
- Estimate traffic growth
- Budget for higher tiers if needed
- Set up auto-scaling alerts

---

## 💰 Cost Breakdown

| Service | Free Tier | Recommended | Cost |
|---------|-----------|------------|------|
| **Railway Backend** | None | Starter | $5-20/month |
| **Vercel Frontend** | Yes | Pro | $20/month |
| **MongoDB Atlas** | Yes (512MB) | Shared | Free-$57/month |
| **Gemini API** | Free | Pay as you go | $0-10/month |
| **Total** | $0-10/month | $25-50/month | Varies |

---

## 📞 Support

- **Railway Docs**: https://docs.railway.app
- **Vercel Docs**: https://vercel.com/docs
- **MongoDB Docs**: https://docs.mongodb.com
- **FastAPI Docs**: https://fastapi.tiangolo.com

---

## 🎉 Success!

Once everything is deployed and working:

1. ✅ Share your Vercel URL with others
2. ✅ Share backend API docs at `/docs` endpoint
3. ✅ Monitor performance on both platforms
4. ✅ Celebrate! 🚀

---

**Created**: 2026-04-29  
**Last Updated**: 2026-04-29  
**Status**: Production Ready ✅
