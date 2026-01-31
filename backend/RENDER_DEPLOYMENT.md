# Deploying Backend to Render - Step-by-Step Guide

## Prerequisites
- A Render account (sign up at https://render.com)
- Your backend code pushed to a Git repository (GitHub, GitLab, or Bitbucket)

## Step 1: Prepare Your Repository

The following files have been created in your backend directory:
- ✅ `render.yaml` - Render service configuration
- ✅ `build.sh` - Build script for installing dependencies
- ✅ `requirements.txt` - Updated with gunicorn

Make sure to commit and push these files to your Git repository.

## Step 2: Create a New Web Service on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** button → Select **"Web Service"**
3. Connect your Git repository
4. Configure the service:
   - **Name**: `fortex26-backend` (or your preferred name)
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: `fortex26/backend` (if backend is in a subdirectory)
   - **Runtime**: Python 3
   - **Build Command**: `./build.sh`
   - **Start Command**: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`

## Step 3: Configure Environment Variables

In the Render dashboard, add the following environment variables:

### Required Variables

| Key | Value | Notes |
|-----|-------|-------|
| `OPENAI_API_KEY` | `sk-proj-...` | Your OpenAI API key (required for AI analysis) |
| `FRONTEND_URL` | `https://your-frontend.vercel.app` | Your deployed frontend URL (comma-separated if multiple) |

### Optional Variables (ZAP Scanning)

> **Note**: ZAP scanning is now **optional**. If you don't configure these variables, the backend will work but skip ZAP-based vulnerability scanning.

| Key | Value | Notes |
|-----|-------|-------|
| `ZAP_API_KEY` | (optional) | Only if using cloud-hosted ZAP |
| `ZAP_PROXY_URL` | (optional) | Only if using cloud-hosted ZAP |
| `ZAP_PROXY` | (optional) | Only if using cloud-hosted ZAP |

## Step 4: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Run `build.sh` to install dependencies
   - Start your FastAPI app with uvicorn
3. Monitor the deployment logs for any errors

## Step 5: Get Your Backend URL

Once deployed, Render will provide a URL like:
```
https://fortex26-backend.onrender.com
```

## Step 6: Update Your Frontend

Update your frontend to use the new backend URL:
- Replace `http://localhost:8000` with `https://fortex26-backend.onrender.com`

## Step 7: Test Your Deployment

Test the following endpoints:

1. **Health Check**:
   ```
   GET https://fortex26-backend.onrender.com/health
   ```
   Should return: `{"status": "healthy", "active_scans": 0}`

2. **Start a Scan**:
   ```
   POST https://fortex26-backend.onrender.com/attack
   Body: {"url": "https://example.com"}
   ```

## Important Notes

### Free Tier Limitations
- **Spin down after inactivity**: Free services sleep after 15 minutes of inactivity
- **First request after sleep**: Takes 30-60 seconds to wake up
- **Monthly usage**: 750 hours/month free

### CORS Configuration
The backend now accepts frontend URLs from the `FRONTEND_URL` environment variable. Make sure to set this to your deployed frontend URL.

### ZAP Scanning (Optional)
- ZAP scanning is **disabled by default** on cloud deployment
- The backend will work without ZAP, but with limited vulnerability scanning
- To enable ZAP scanning, you need to set up a cloud-hosted ZAP instance and configure the environment variables

## Troubleshooting

### Build Fails
- Check that `build.sh` has execute permissions
- Verify all dependencies in `requirements.txt` are available

### App Crashes on Startup
- Check environment variables are set correctly
- Review Render logs for error messages
- Ensure port binding uses `$PORT` environment variable

### CORS Errors
- Verify `FRONTEND_URL` environment variable includes your frontend domain
- Check that frontend is making requests to the correct backend URL

## Next Steps

After successful deployment:
1. Update your frontend's API endpoint
2. Test all functionality end-to-end
3. Monitor Render logs for any issues
4. Consider upgrading to a paid plan to avoid spin-down delays
