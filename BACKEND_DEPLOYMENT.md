# Backend Deployment Guide for SentinelAI

## Problem: "Failed to fetch" Error

The frontend is deployed on Netlify but the Flask backend is not deployed. Netlify only hosts static frontend files, not Python/Flask servers. The frontend needs a running backend to handle API calls.

## Solution: Deploy Backend Separately

### Option 1: Render (Recommended - Free Tier Available)

Render offers free hosting for Flask applications.

#### Steps:
1. Go to [render.com](https://render.com) and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `python backend/app.py`
   - **Runtime**: Python 3.10
5. Click "Deploy Web Service"

#### After Deployment:
1. Copy your Render backend URL (e.g., `https://sentinelai-backend.onrender.com`)
2. Update `netlify.toml` redirect URL
3. Add `VITE_API_URL` environment variable in Netlify

### Option 2: Railway

Railway also offers free hosting for Flask apps.

#### Steps:
1. Go to [railway.app](https://railway.app) and sign up
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect Python
5. Set start command: `python backend/app.py`
6. Deploy

### Option 3: PythonAnywhere

PythonAnywhere is optimized for Python hosting.

#### Steps:
1. Go to [pythonanywhere.com](https://pythonanywhere.com) and sign up
2. Create a "Web" app
3. Choose Flask framework
4. Upload your code or connect via git
5. Configure WSGI file

### Option 4: Local Development (For Testing)

If you want to test the deployed frontend with a local backend:

1. Run the backend locally:
```bash
cd backend
pip install -r requirements.txt
python app.py
```

2. Use ngrok to expose your local backend:
```bash
# Install ngrok
# Then run:
ngrok http 5000
```

3. Copy the ngrok URL and use it for API calls

## Configuration Steps After Backend Deployment

### 1. Update netlify.toml
Replace the placeholder URL with your actual backend URL:

```toml
[[redirects]]
  from = "/api/*"
  to = "https://your-actual-backend-url.com/api/:splat"
  status = 200
  force = true
```

### 2. Set Environment Variable in Netlify
1. Go to Netlify dashboard → Site settings → Environment variables
2. Add: `VITE_API_URL = https://your-actual-backend-url.com`
3. Redeploy the frontend

### 3. Test the Connection
1. Access your Netlify frontend
2. Try logging in with seeded users:
   - john / password123
   - alice / password123
   - david / password123
   - sam / password123

## Quick Fix: Use Render (Easiest Free Option)

Render is the easiest free option for Flask deployment:

1. **Create Render Account**: https://render.com
2. **Deploy Backend**:
   - Connect GitHub repo
   - Build: `pip install -r backend/requirements.txt`
   - Start: `python backend/app.py`
3. **Get Backend URL**: Render will provide a URL like `https://sentinelai-xyz.onrender.com`
4. **Update Configuration**:
   - Edit `netlify.toml` with your Render URL
   - Add `VITE_API_URL` in Netlify environment variables
5. **Redeploy Frontend**: Netlify will rebuild with new configuration

## Alternative: Single-File Backend for Simpler Deployment

If deployment is too complex, I can create a simplified version that works with serverless functions or easier deployment options.
