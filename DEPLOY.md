# Deploying Masidy to Render

This guide explains how to deploy the Masidy AI Agent Platform to Render.

## Prerequisites

- A [Render account](https://render.com)
- GitHub repository connected to Render

## Option 1: Blueprint Deployment (Recommended)

The easiest way to deploy is using the `render.yaml` blueprint:

1. **Connect GitHub Repository**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Blueprint"
   - Select your GitHub repository (`masidyai/agent`)
   - Render will detect `render.yaml` and show the services

2. **Review Services**
   - Backend: `masidy-backend` (Python)
   - Frontend: `masidy-frontend` (Node.js)
   - Database: `masidy-db` (PostgreSQL)

3. **Deploy**
   - Click "Apply" to create all services
   - Wait for builds to complete (5-10 minutes)

4. **Access Your App**
   - Backend: `https://masidy-backend.onrender.com`
   - Frontend: `https://masidy-frontend.onrender.com`

## Option 2: Manual Deployment

### Step 1: Create PostgreSQL Database

1. Go to Render Dashboard → "New" → "PostgreSQL"
2. Configure:
   - **Name**: `masidy-db`
   - **Database**: `masidy`
   - **User**: `masidy`
   - **Region**: Oregon (or your preferred region)
   - **Plan**: Free
3. Click "Create Database"
4. Copy the **Internal Database URL** for later

### Step 2: Deploy Backend

1. Go to Render Dashboard → "New" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `masidy-backend`
   - **Root Directory**: `backend_api`
   - **Runtime**: Python 3
   - **Build Command**: `chmod +x build.sh && ./build.sh`
   - **Start Command**: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

4. Add Environment Variables:
   ```
   DATABASE_URL = <Internal Database URL from Step 1>
   SECRET_KEY = <click "Generate" for a random key>
   CORS_ORIGINS = https://masidy-frontend.onrender.com,http://localhost:3000
   DEBUG = false
   APP_NAME = Masidy API
   ACCESS_TOKEN_EXPIRE_MINUTES = 30
   REFRESH_TOKEN_EXPIRE_DAYS = 7
   PYTHON_VERSION = 3.11.0
   ```

5. Click "Create Web Service"

### Step 3: Deploy Frontend

1. Go to Render Dashboard → "New" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `masidy-frontend`
   - **Root Directory**: `masidy_frontend`
   - **Runtime**: Node
   - **Build Command**: `npm ci && npm run build`
   - **Start Command**: `npm start`
   - **Plan**: Free

4. Add Environment Variables:
   ```
   NEXT_PUBLIC_API_URL = https://masidy-backend.onrender.com
   NODE_VERSION = 18
   ```

5. Click "Create Web Service"

## Verifying Deployment

### Backend Health Check

```bash
curl https://masidy-backend.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "healthy"
}
```

### API Endpoints

```bash
# Get billing plans
curl https://masidy-backend.onrender.com/api/v1/billing/plans

# Visual builder components
curl https://masidy-backend.onrender.com/api/v1/visual-builder/components
```

### Frontend

Visit `https://masidy-frontend.onrender.com` in your browser.

## Troubleshooting

### Backend Build Fails

1. Check build logs in Render Dashboard
2. Ensure `requirements.txt` has all dependencies
3. Verify `PYTHON_VERSION` is set to `3.11.0`

### Database Connection Issues

1. Verify `DATABASE_URL` is set correctly
2. Check that PostgreSQL service is running
3. Ensure you're using the **Internal Database URL** (not External)

### Frontend Can't Connect to Backend

1. Check `NEXT_PUBLIC_API_URL` is set correctly
2. Verify CORS is configured: `CORS_ORIGINS` should include frontend URL
3. Check backend logs for CORS errors

### Free Tier Limitations

Render's free tier has some limitations:
- Services spin down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds (cold start)
- PostgreSQL free tier expires after 90 days

For production, consider upgrading to paid plans.

## Environment Variables Reference

### Backend

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | `postgres://user:pass@host/db` |
| `SECRET_KEY` | JWT signing key | Auto-generated |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | `https://frontend.onrender.com` |
| `DEBUG` | Enable debug mode | `false` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT access token expiry | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiry | `7` |

### Frontend

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `https://backend.onrender.com` |
| `NODE_VERSION` | Node.js version | `18` |

## Updating Deployment

Render automatically deploys on push to `main` branch:

```bash
git add .
git commit -m "Update deployment"
git push origin main
```

Render will automatically rebuild and redeploy both services.

## Custom Domain

1. Go to your service in Render Dashboard
2. Click "Settings" → "Custom Domains"
3. Add your domain (e.g., `api.masidy.ai`, `app.masidy.ai`)
4. Update DNS records as instructed
5. Update `CORS_ORIGINS` and `NEXT_PUBLIC_API_URL` with new domains
