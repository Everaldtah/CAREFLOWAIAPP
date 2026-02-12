# CareFlow AI - Railway Deployment Guide

## 🚀 Complete Railway Deployment Guide

This guide covers deployment of CareFlow AI to Railway.cloud with custom domain `careflowai.veraldlabs.co.uk`.

---

## Prerequisites

- Railway account with project created
- Services created: backend, frontend, PostgreSQL, Redis
- GitHub repository: Everaldtah/CAREFLOWAIAPP

---

## 📋 Project Structure

The Railway project has been created with:
- **Backend Service** (Python/FastAPI)
- **Frontend Service** (Next.js)
- **PostgreSQL Database**
- **Redis Cache**

---

## 🔧 Backend Environment Variables

Add these variables to the **Backend Service**:

| Variable | Value | Source |
|-----------|--------|--------|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` | Auto-linked from careflow-postgres |
| `REDIS_URL` | `${{Redis.REDIS_URL}}` | Auto-linked from careflow-redis |
| `REDIS_CACHE_URL` | `${{Redis.REDIS_URL}}` | Auto-linked from careflow-redis |
| `REDIS_AGENT_STATE_URL` | `${{Redis.REDIS_URL}}` | Auto-linked from careflow-redis |
| `APP_ENV` | `production` | Manual |
| `APP_URL` | `https://careflowai.veraldlabs.co.uk` | Manual |
| `API_URL` | `https://careflow-backend.onrender.com` | Manual |
| `SECRET_KEY` | `[Click Generate in Railway]` | Generate in Railway |
| `ENCRYPTION_KEY` | `[Click Generate in Railway]` | Generate in Railway |
| `OPENAI_API_KEY` | Your OpenAI API key | Manual |

### Backend URLs:
- **Railway URL**: Provided after deployment
- **Custom Domain**: `api.careflowai.veraldlabs.co.uk`

---

## 🔧 Frontend Environment Variables

Add these variables to the **Frontend Service**:

| Variable | Value |
|-----------|--------|
| `NODE_ENV` | `production` |
| `NEXT_PUBLIC_APP_URL` | `https://careflowai.veraldlabs.co.uk` |
| `NEXT_PUBLIC_API_URL` | `https://api.careflowai.veraldlabs.co.uk` |

### Frontend URLs:
- **Railway URL**: Provided after deployment
- **Custom Domain**: `careflowai.veraldlabs.co.uk`

---

## 🌐 Custom Domains

### Backend Domain:
1. Go to **Backend Service** → **Settings** → **Domains**
2. Click **Add Domain**
3. Enter: `api.careflowai.veraldlabs.co.uk`

### Frontend Domain:
1. Go to **Frontend Service** → **Settings** → **Domains**
2. Click **Add Domain**
3. Enter: `careflowai.veraldlabs.co.uk`

---

## 🗄️ Database Migrations

Once services are running with environment variables configured:

### Option 1: Via Railway CLI (if authentication works)
```bash
railway run backend
alembic upgrade head
```

### Option 2: Via Railway Dashboard (Recommended)
1. Go to **Backend Service**
2. Click **"Deployments"** tab
3. Click **"New Deployment"** → **"Variables"**
4. Add variable: `RUN_MIGRATIONS` = `alembic upgrade head`
5. Click **"Save & Deploy"**

---

## ✅ Verification Steps

### 1. Check Backend Health
```bash
curl https://api.careflowai.veraldlabs.co.uk/health
# Should return: {"status":"healthy"}
```

### 2. Check Frontend
```bash
curl https://careflowai.veraldlabs.co.uk
# Should return CareFlow AI HTML
```

### 3. Check API Documentation
Visit: https://api.careflowai.veraldlabs.co.uk/docs

---

## 🔧 Service Configuration

### Backend Service:
- **Name**: careflow-backend
- **Root Directory**: backend
- **Dockerfile**: backend/Dockerfile
- **Start Command**: Python uvicorn server
- **Port**: 8000 (auto-assigned)

### Frontend Service:
- **Name**: frontend
- **Root Directory**: frontend
- **Dockerfile**: frontend/Dockerfile
- **Start Command**: npm start
- **Port**: 3000 (auto-assigned)

---

## 💡 Important Notes

1. **DNS Must Be Propagated**
   - CNAME records for `careflowai.veraldlabs.co.uk` and `api.careflowai.veraldlabs.co.uk` must be fully propagated
   - Check propagation at: https://dnschecker.org/
   - Usually takes 10-30 minutes, up to 48 hours

2. **PostgreSQL & Redis**
   - Already added to your Railway project
   - Will be auto-linked to backend via environment variables

3. **OpenAI API Key**
   - Required for AI features (triage, scribe, etc.)
   - Add your key to `OPENAI_API_KEY` variable

4. **Security Keys**
   - `SECRET_KEY` and `ENCRYPTION_KEY` are generated automatically by Railway
   - Click "Generate" button in Railway UI

---

## 🚨 Troubleshooting

### Backend Issues:
```bash
# Check logs in Railway dashboard
railway logs backend

# Restart service
railway restart backend
```

### Frontend Issues:
```bash
# Check logs
railway logs frontend

# Restart service
railway restart frontend
```

### Domain Not Working:
1. Verify DNS records are correct
2. Check domain configuration in Railway
3. Wait for full DNS propagation

---

## 📞 Support

- **Railway Documentation**: https://docs.railway.app/
- **Railway Status**: https://status.railway.app/
- **GitHub Issues**: Check repository for updates

---

**Deployment Status**: ✅ Ready for configuration
