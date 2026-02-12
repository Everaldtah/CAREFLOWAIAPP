# Quick Start: Deploy CareFlow AI to Railway

Deploy CareFlow AI to careflowai.veraldlabs.co.uk in ~30 minutes.

---

## Prerequisites

- GitHub account
- Railway account (free tier: https://railway.app/)
- OpenAI API key (for AI features)
- Access to veraldlabs.co.uk DNS management

---

## Step-by-Step Deployment

### Step 1: Push Code to GitHub (5 minutes)

```bash
cd C:/Users/evera/careflow-ai

# Initialize git (if not already done)
git init
git add .
git commit -m "Prepare for Railway deployment"

# Create a new repository on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/careflow-ai.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Railway (10 minutes)

#### A. Create Railway Project

1. Go to https://railway.app/
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your `careflow-ai` repository
4. Click **Deploy Now**

#### B. Add Services

Railway will detect services. If not, add manually:

1. **PostgreSQL Database**
   - Click **New Service** → **Database** → **PostgreSQL**

2. **Redis**
   - Click **New Service** → **Add Redis** → **Upstash Redis** (free)

3. **Backend** (if not auto-detected)
   - Click **New Service** → **Deploy from GitHub**
   - Select `careflow-ai` repo
   - Set root directory to `backend`
   - Set start command to: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Frontend** (if not auto-detected)
   - Click **New Service** → **Deploy from GitHub**
   - Select `careflow-ai` repo
   - Set root directory to `frontend`
   - Set start command to: `npm start`

### Step 3: Configure Environment Variables (5 minutes)

#### Backend Variables

Click on **Backend Service** → **Variables** → **New Variable**:

```bash
# Database & Redis (Railway auto-links these)
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
REDIS_CACHE_URL=${{Redis.REDIS_URL}}
REDIS_AGENT_STATE_URL=${{Redis.REDIS_URL}}

# Application
APP_ENV=production
APP_URL=https://careflowai.veraldlabs.co.uk
API_URL=https://your-backend-name.up.railway.app

# Security (Click "Generate" for these in Railway)
SECRET_KEY=[Click Generate]
SECRET_KEY_REFRESH=[Click Generate]
ENCRYPTION_KEY=[Click Generate]

# AI/LLM
OPENAI_API_KEY=sk-your-actual-openai-key-here
LLM_MODEL=gpt-4-turbo-preview

# Email (optional)
SMTP_HOST=smtp.resend.com
SMTP_PORT=587
```

#### Frontend Variables

Click on **Frontend Service** → **Variables** → **New Variable**:

```bash
NODE_ENV=production
NEXT_PUBLIC_APP_URL=https://careflowai.veraldlabs.co.uk
NEXT_PUBLIC_API_URL=https://your-backend-name.up.railway.app
```

### Step 4: Run Database Migrations (3 minutes)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Select your project
railway project

# Run migrations
railway run bash
alembic upgrade head
exit
```

### Step 5: Configure Custom Domains (5 minutes)

#### A. In Railway

1. **Frontend Service** → **Settings** → **Domains**
2. Click **Add Custom Domain**
3. Enter: `careflowai.veraldlabs.co.uk`
4. Click **Add**

5. **Backend Service** → **Settings** → **Domains**
6. Click **Add Custom Domain**
7. Enter: `api.careflowai.veraldlabs.co.uk`
8. Click **Add**

#### B. In Your DNS Provider

Add these DNS records for veraldlabs.co.uk:

| Type  | Name            | Value              | TTL  |
|-------|-----------------|--------------------|------|
| CNAME | careflowai      | cname.railway.app  | 3600 |
| CNAME | api.careflowai  | cname.railway.app  | 3600 |

### Step 6: Verify Deployment (2 minutes)

```bash
# Test frontend
curl https://careflowai.veraldlabs.co.uk

# Test backend health
curl https://api.careflowai.veraldlabs.co.uk/health

# Test API docs (open in browser)
# https://api.careflowai.veraldlabs.co.uk/docs
```

---

## Access Your Application

| What | URL |
|------|-----|
| **Frontend** | https://careflowai.veraldlabs.co.uk |
| **Backend API** | https://api.careflowai.veraldlabs.co.uk |
| **API Docs** | https://api.careflowai.veraldlabs.co.uk/docs |
| **Health Check** | https://api.careflowai.veraldlabs.co.uk/health |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Build fails | Check Railway logs, verify dependencies |
| Database error | Verify DATABASE_URL is set correctly |
| 404 on custom domain | Wait 10-30 minutes for DNS propagation |
| AI features not working | Verify OPENAI_API_KEY is set |

---

## Cost Estimate (Railway Free Tier)

- **Free Tier Credit**: $5/month
- **Estimated Cost**: $0-10/month depending on usage
- **Overage**: Backend ~$5-10/mo, Frontend ~$5/mo

---

## Production Checklist

- [ ] Code pushed to GitHub
- [ ] Railway project created
- [ ] PostgreSQL database added
- [ ] Redis cache added
- [ ] Backend deployed
- [ ] Frontend deployed
- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] Custom domains added in Railway
- [ ] DNS records added
- [ ] Frontend accessible at careflowai.veraldlabs.co.uk
- [ ] Backend health check passing
- [ ] OpenAI API key configured

---

## Next Steps

1. **Create admin user** via the frontend registration
2. **Test AI features** with your OpenAI API key
3. **Set up monitoring** in Railway dashboard
4. **Configure backups** (Railway auto-backups PostgreSQL)

---

## Need Help?

- **Railway Documentation**: https://docs.railway.app/
- **Database Guide**: See DATABASE_MIGRATION_GUIDE.md
- **DNS Guide**: See DNS_CONFIGURATION_GUIDE.md
- **Full Deployment Guide**: See RAILWAY_DEPLOYMENT.md

---

**You're all set! 🚀**
