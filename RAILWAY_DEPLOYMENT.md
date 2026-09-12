# Railway Full-Stack Deployment Guide

## Why Railway?

Railway is the best free full-stack platform for your Flask + React application:
- **Free tier available** ($5/month credit)
- **Hosts both frontend and backend** on one platform
- **Easy GitHub integration**
- **Automatic SSL and domain**
- **Supports Docker and multiple services**

## Deployment Steps

### 1. Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. You'll get $5 free credit monthly

### 2. Create New Project
1. Click "New Project" 
2. Select "Deploy from GitHub repo"
3. Choose your repository: `prithikaam/https-github.com-prithikaam-Sentinel-AI`
4. Railway will analyze your repository

### 3. Configure Services

Railway will auto-detect your services. You'll need to configure two:

#### Backend Service (Flask)
1. Click on the Python service
2. **Build Command**: `pip install -r backend/requirements.txt`
3. **Start Command**: `python backend/app.py`
4. **Environment Variables**:
   - Add `PYTHONUNBUFFERED=1`
   - Add `FLASK_ENV=production`

#### Frontend Service (React)
1. Click "New Service" → "GitHub Repo"
2. Select the same repository
3. **Build Command**: `cd frontend && npm install && npm run build`
4. **Start Command**: Use a static file server or configure as static site
5. **Environment Variables**:
   - Add `VITE_API_URL=${{BACKEND_URL}}` (Railway auto-replaces this)

### 4. Connect Services
1. Go to your frontend service
2. Click "Variables" tab
3. Add `VITE_API_URL` and set it to your backend service URL
4. Railway provides variable references like `${{BACKEND_SERVICE_URL}}`

### 5. Deploy
1. Click "Deploy" for both services
2. Wait for deployment (2-3 minutes each)
3. Railway will provide URLs for both services

### 6. Access Your App
- **Frontend URL**: Railway provides a domain like `sentinelai-frontend.railway.app`
- **Backend URL**: Railway provides a domain like `sentinelai-backend.railway.app`

## Alternative: Single Docker Service

If you prefer a single service, Railway can run the Dockerfile we created:

1. Create one service from your repo
2. **Build Command**: Leave empty (Dockerfile will be used)
3. **Start Command**: Leave empty (Dockerfile CMD will be used)
4. Railway will build and run the Docker container

## Environment Variables

Set these in Railway dashboard:

### Backend
- `PYTHONUNBUFFERED=1`
- `FLASK_ENV=production`
- `PORT=5000`

### Frontend
- `VITE_API_URL=https://your-backend-url.railway.app`

## Troubleshooting

### Backend Not Starting
- Check logs in Railway dashboard
- Ensure Python version is 3.10+
- Verify all dependencies are in requirements.txt

### Frontend API Errors
- Verify `VITE_API_URL` is set correctly
- Check that backend service is running
- Look at browser console for specific errors

### Port Issues
- Railway automatically assigns ports
- Update Flask to use `PORT` environment variable:
  ```python
  import os
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)
  ```

## Cost

- **Free tier**: $5/month credit (usually sufficient for small apps)
- **Beyond free**: Pay-as-you-go based on usage
- Typical small app: $0-5/month

## Advantages Over Netlify + Render

- Single platform for both services
- Easier management
- Built-in service discovery
- Better integration between frontend and backend
- Simplified deployment process
