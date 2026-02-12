# CareFlow AI - Railway Deployment Guide

## Deploy to careflowai.veraldlabs.co.uk

This guide will help you deploy CareFlow AI to Railway.cloud and connect it to your subdomain.

---

## Prerequisites

1. Railway Account (free tier available): https://railway.app/
2. GitHub Account (for code repository)
3. CareFlow AI source code
4. OpenAI API Key (for AI features)

---

## Step 1: Push Code to GitHub

```bash
cd C:/Users/evera/careflow-ai
git init
git add .
git commit -m "Initial commit for Railway deployment"
# Create a new repository on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/careflow-ai.git
git push -u origin main
```

---

## Step 2: Deploy to Railway

### Option A: Deploy via Railway CLI (Recommended)

1. Install Railway CLI:
```bash
# Windows (using PowerShell)
npm install -g @railway/cli

# Or download from: https://github.com/railwayapp/cli
```

2. Login to Railway:
```bash
railway login
```

3. Initialize project:
```bash
cd C:/Users/evera/careflow-ai
railway init
```

4. Add PostgreSQL Database:
```bash
railway add postgresql
```

5. Add Redis:
```bash
railway add redis
```

6. Deploy Backend:
```bash
cd backend
railway up --service=backend
```

7. Deploy Frontend:
```bash
cd ../frontend
railway up --service=frontend
```

### Option B: Deploy via Railway Dashboard

1. Go to https://railway.app/
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your careflow-ai repository
4. Railway will auto-detect services

---

## Step 3: Configure Environment Variables

### Backend Environment Variables

Go to your backend service in Railway and add these variables:

```bash
# Database (Railway provides DATABASE_URL automatically)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Redis (Railway provides REDIS_URL automatically)
REDIS_URL=${{Redis.REDIS_URL}}
REDIS_CACHE_URL=${{Redis.REDIS_URL}}
REDIS_AGENT_STATE_URL=${{Redis.REDIS_URL}}

# Application
APP_ENV=production
APP_URL=https://careflowai.veraldlabs.co.uk
API_URL=https://your-backend-url.railway.app

# Security (Generate these with: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=your-secret-key-here
SECRET_KEY_REFRESH=your-refresh-key-here
ENCRYPTION_KEY=your-encryption-key-hex-here

# AI/LLM
OPENAI_API_KEY=sk-your-openai-api-key-here

# Email (optional)
SMTP_HOST=smtp.resend.com
SMTP_PORT=587
SMTP_USER=your-smtp-user
SMTP_PASSWORD=your-smtp-password
SMTP_FROM=noreply@veraldlabs.co.uk

# Logging
LOG_LEVEL=INFO
SENTRY_ENVIRONMENT=production
```

### Frontend Environment Variables

```bash
NODE_ENV=production
NEXT_PUBLIC_APP_URL=https://careflowai.veraldlabs.co.uk
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
NEXT_PUBLIC_ENABLE_ANALYTICS=false
```

---

## Step 4: Get Railway URLs

After deployment, Railway provides:
- Backend URL: `https://your-backend-name.up.railway.app`
- Frontend URL: `https://your-frontend-name.up.railway.app`

Note these URLs for the next step.

---

## Step 5: Configure Custom Domain

### Add Domain in Railway

1. Go to your service settings in Railway dashboard
2. Click "Domains" → "Generate Domain"
3. For backend: Click "Add Custom Domain" → `api.careflowai.veraldlabs.co.uk`
4. For frontend: Click "Add Custom Domain" → `careflowai.veraldlabs.co.uk`

### Configure DNS

Go to your VeraldLabs DNS management (where veraldlabs.co.uk is registered) and add:

| Type  | Name                      | Value                          | TTL  |
|-------|---------------------------|--------------------------------|------|
| CNAME | careflowai                | [your-frontend-name].up.railway.app | 3600 |
| CNAME | api.careflowai            | [your-backend-name].up.railway.app | 3600 |

Or if using A records:

| Type  | Name        | Value                 | TTL  |
|-------|-------------|-----------------------|------|
| CNAME | careflowai  | cname.railway.app     | 3600 |
| CNAME | api         | cname.railway.app     | 3600 |

---

## Step 6: Run Database Migrations

After the PostgreSQL database is created in Railway:

```bash
# Get the database connection string from Railway dashboard
# Then run Alembic migrations

cd backend

# Set DATABASE_URL from Railway
export DATABASE_URL="postgresql://user:password@host:port/dbname"

# Run migrations
alembic upgrade head
```

Or use Railway CLI to run in the deployed environment:

```bash
railway run bash
alembic upgrade head
exit
```

---

## Step 7: Verify Deployment

### Test Backend Health

```bash
curl https://api.careflowai.veraldlabs.co.uk/health
# Should return: {"status":"healthy"}
```

### Test API Docs

Visit: `https://api.careflowai.veraldlabs.co.uk/docs`

### Test Frontend

Visit: `https://careflowai.veraldlabs.co.uk`

---

## Railway Service URLs Summary

| Service | Railway URL | Custom Domain |
|---------|-------------|---------------|
| Backend API | `https://[backend].up.railway.app` | `https://api.careflowai.veraldlabs.co.uk` |
| Frontend | `https://[frontend].up.railway.app` | `https://careflowai.veraldlabs.co.uk` |

---

## Troubleshooting

### Database Connection Issues

1. Check DATABASE_URL is set correctly
2. Verify PostgreSQL service is running in Railway
3. Run `alembic upgrade head` to create tables

### Frontend Build Fails

1. Check NODE_ENV is set to "production"
2. Verify NEXT_PUBLIC_API_URL points to correct backend URL
3. Check Railway build logs

### Custom Domain Not Working

1. Wait 10-30 minutes for DNS propagation
2. Verify DNS records match Railway's requirements
3. Check domain configuration in Railway dashboard

### OpenAI API Not Working

1. Verify OPENAI_API_KEY is set correctly
2. Check API key has available credits
3. Check Railway logs for errors

---

## Cost Estimate (Railway Free Tier)

- **Free Tier**: $5/month credit
- **PostgreSQL**: Included in free tier
- **Redis**: ~$0 (free tier)
- **Backend**: ~$0-5/month (depending on usage)
- **Frontend**: ~$0-5/month (depending on usage)

---

## Alternative: Render Deployment

If Railway doesn't work, use Render:

1. Go to https://render.com/
2. Connect GitHub repository
3. Create services:
   - PostgreSQL Database
   - Redis (through Upstash or Render)
   - Web Service (Backend)
   - Static Site (Frontend)

---

## Alternative: Fly.io Deployment

1. Install `flyctl` CLI
2. `fly launch` in backend directory
3. `fly postgres create` for database
4. `fly deploy` to deploy

---

## Next Steps

After successful deployment:

1. Create admin user via the frontend
2. Configure OpenAI API key for AI features
3. Set up email for notifications (optional)
4. Monitor logs in Railway dashboard
5. Set up monitoring (optional with Sentry)

---

Need help? Check Railway docs: https://docs.railway.app/
