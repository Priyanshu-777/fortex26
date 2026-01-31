# Quick Start: Deploy to Render

## 1. Push Your Code to Git

Make sure all files are committed and pushed to your GitHub repository:

```bash
git add .
git commit -m "Prepare backend for Render deployment"
git push origin main
```

## 2. Create Render Web Service

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `fortex26-backend`
   - **Root Directory**: `fortex26/backend` (if in subdirectory)
   - **Runtime**: Python 3
   - **Build Command**: `./build.sh`
   - **Start Command**: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`

## 3. Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**:

- `OPENAI_API_KEY` = `your-openai-api-key`
- `FRONTEND_URL` = `http://localhost:5173` (update after frontend deployment)

## 4. Deploy

Click **"Create Web Service"** and wait for deployment to complete (~2-5 minutes).

## 5. Get Your Backend URL

Copy the URL from Render dashboard (e.g., `https://fortex26-backend.onrender.com`)

## 6. Test

```bash
curl https://fortex26-backend.onrender.com/health
```

Expected response:
```json
{"status": "healthy", "active_scans": 0}
```

## 7. Update Frontend

Update your frontend to use the new backend URL instead of `http://localhost:8000`.

---

**That's it!** Your backend is now deployed on Render. 🎉

For detailed instructions, see [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md)
