# Deployment Guide for SentinelAI

## Deployment Errors Fixed

The following deployment issues have been identified and resolved:

### 1. Backend Host Binding Issue
**Problem**: Flask was configured to run on `127.0.0.1` (localhost only), preventing external connections in production.

**Solution**: Changed `app.run(host='127.0.0.1', ...)` to `app.run(host='0.0.0.0', ...)` in `backend/app.py` to accept external connections.

### 2. Hardcoded API URLs
**Problem**: Frontend components had hardcoded `http://127.0.0.1:5000` URLs that wouldn't work in production environments.

**Solution**: 
- Created `frontend/src/config.js` to manage API URL via environment variable
- Updated all frontend components (Login, Dashboard, Simulator, Assistant, KyberVisualizer) to use the configurable API URL
- Added `.env.example` file for configuration template

### 3. Missing Deployment Configuration
**Problem**: No Docker or deployment configuration files existed.

**Solution**: Created deployment files:
- `Dockerfile` - Multi-stage Docker build for production
- `docker-compose.yml` - Docker Compose configuration
- `.dockerignore` - Docker build optimizations
- `vercel.json` - Vercel deployment configuration

## Deployment Options

### Option 1: Docker Deployment

#### Build and Run with Docker
```bash
# Build the Docker image
docker build -t sentinelai .

# Run the container
docker run -p 5000:5000 sentinelai
```

#### Build and Run with Docker Compose
```bash
# Build and start services
docker-compose up --build

# Run in detached mode
docker-compose up -d --build

# Stop services
docker-compose down
```

### Option 2: Vercel Deployment

#### Prerequisites
- Install Vercel CLI: `npm i -g vercel`
- Link your project to Vercel

#### Deploy to Vercel
```bash
# Deploy to Vercel
vercel

# Deploy to production
vercel --prod
```

**Note**: For Vercel deployment, you may need to adjust the backend to work with serverless functions, as Vercel doesn't support long-running Flask servers directly.

### Option 3: Traditional Server Deployment

#### Backend Deployment
```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Run the Flask server
python backend/app.py
```

The server will now run on `0.0.0.0:5000` and accept external connections.

#### Frontend Deployment
```bash
cd frontend
npm install
npm run build
```

Serve the `dist` folder using a web server like Nginx or Apache.

## Environment Configuration

### Local Development
Create a `.env` file in the `frontend` directory:
```
VITE_API_URL=http://127.0.0.1:5000
```

### Production
Set the environment variable to your production backend URL:
```
VITE_API_URL=https://your-backend-domain.com
```

## Testing the Deployment

1. Start the backend server
2. Build and serve the frontend
3. Access the application at the configured URL
4. Test login functionality with seeded users:
   - john (password123)
   - alice (password123)
   - david (password123)
   - sam (password123)

## Troubleshooting

### Backend Not Accessible
- Ensure the backend is running on `0.0.0.0:5000`
- Check firewall settings
- Verify port 5000 is not blocked

### Frontend API Errors
- Check that `VITE_API_URL` is set correctly
- Verify the backend is running and accessible
- Check browser console for CORS errors

### Docker Build Issues
- Ensure Docker is running
- Check that all files are included (not in .dockerignore)
- Verify Python and Node versions in Dockerfile
