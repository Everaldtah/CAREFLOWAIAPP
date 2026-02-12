# 🌐 Deploy CareFlow AI on careflowai subdomain

## Quick Start for Your Agent

Since your web server is already configured with PHP and logging, follow these steps to deploy CareFlow AI under the `careflowai` subdomain.

---

## 📋 What Your Agent Needs to Do

### Option 1: Docker Deployment (Recommended - Fastest)

```bash
# SSH into your web server
ssh root@77.68.64.45

# Upload deployment package
scp -r DEPLOYMENT_PACKAGE root@77.68.64.45:/opt/careflow-ai-deploy/

# SSH and deploy
ssh root@77.68.64.45
cd /opt/careflow-ai-deploy

# Extract and configure
unzip careflow-ai-deploy.zip
cd careflow-ai-deploy

# Edit environment for your subdomain
nano .env.production

# Update these lines with your subdomain:
DOMAIN=careflowai.veraldabs.co.uk
APP_URL=https://careflowai.veraldabs.co.uk
API_URL=https://api.careflowai.veraldabs.co.uk
NEXT_PUBLIC_APP_URL=https://careflowai.veraldabs.co.uk
NEXT_PUBLIC_API_URL=https://api.careflowai.veraldabs.co.uk

# Add your OpenAI API key
OPENAI_API_KEY=sk-your-openai-key-here

# Save and exit
# Run deployment
chmod +x deploy.sh
sudo ./deploy.sh --domain=careflowai.veraldabs.co.uk
```

### Option 2: Manual Configuration

If you prefer to configure Docker containers manually:

```bash
# Create Docker network (if doesn't exist)
docker network create careflow-network

# Run backend
docker run -d \
  --name careflow-backend \
  --network careflow-network \
  -p 8000:8000 \
  -e APP_ENV=production \
  -e DATABASE_URL=postgresql://careflow:password@postgres:5432/careflow_prod \
  -e API_URL=https://api.careflowai.veraldabs.co.uk \
  -e OPENAI_API_KEY=sk-... \
  careflow-ai/backend

# Run frontend
docker run -d \
  --name careflow-frontend \
  --network careflow-network \
  -p 3001:3000 \
  -e NEXT_PUBLIC_APP_URL=https://careflowai.veraldabs.co.uk \
  -e NEXT_PUBLIC_API_URL=https://api.careflowai.veraldabs.co.uk \
  careflow-ai/frontend
```

---

## 📖 DNS Configuration for careflowai Subdomain

Add these DNS records at your registrar (veraldabs.co.uk):

| Type | Name | Value | TTL |
|------|------|-------|-----|
| **A** | `careflowai` | `77.68.64.45` | 3600 |
| **A** | `www` | `77.68.64.45` (optional) | 3600 |
| **A** | `api` | `77.68.64.45` | 3600 |

> **Note**: Your existing website (`veraldabs.co.uk`) will continue working as-is.

---

## 🌐 Nginx Configuration (Already on Your Server)

The Nginx config has been created to reverse proxy CareFlow AI.

### Location Structure:

| Path | Proxies To |
|------|-------------|
| `/` | Redirects to HTTPS |
| `/health` | Backend health endpoint |
| `/api/*` | CareFlow AI Backend API |
| Other | Your existing PHP apps |

### What Gets Proxied:

**careflowai.veraldabs.co.uk** requests go to:
- Frontend: `careflow_frontend` container (port 3001) → CareFlow AI UI
- Backend API: `careflow_backend` container (port 8000) → CareFlow AI API
- Health: `careflow_backend` → Health check endpoint

---

## 🔧 Environment Variables for Subdomain

Update `.env.production` with:

```bash
DOMAIN=careflowai.veraldabs.co.uk
APP_URL=https://careflowai.veraldabs.co.uk
API_URL=https://api.careflowai.veraldabs.co.uk
NEXT_PUBLIC_APP_URL=https://careflowai.veraldabs.co.uk
NEXT_PUBLIC_API_URL=https://api.careflowai.veraldabs.co.uk
CORS_ORIGINS=https://careflowai.veraldabs.co.uk,https://www.veraldabs.co.uk
```

---

## 🚀 Quick Deploy Commands

### Single Command Deployment:
```bash
# Deploy everything at once
curl -fsSL https://raw.githubusercontent.com/your-repo/careflow-ai/main/deploy/deploy.sh | bash -s --domain=careflowai.veraldabs.co.uk
```

### Manual Steps:
1. Upload `DEPLOYMENT_PACKAGE` folder to `/opt/careflow-ai-deploy/`
2. Edit `.env.production` with your subdomain
3. Run: `chmod +x deploy.sh && sudo ./deploy.sh --domain=careflowai.veraldabs.co.uk`

---

## ✅ Verification

After deployment, test:

```bash
# Test frontend
curl -I https://careflowai.veraldabs.co.uk

# Test backend health
curl https://api.careflowai.veraldabs.co.uk/health

# Test API
curl https://api.careflowai.veraldabs.co.uk/docs
```

Expected responses:
- ✅ Frontend returns 200 OK
- ✅ Backend health returns: `{"status":"healthy"}`
- ✅ API docs accessible at /docs

---

## 📱 Troubleshooting

### CareFlow AI Not Loading?

```bash
# Check container status
docker ps | grep careflow

# Check logs
docker logs careflow-backend
docker logs careflow-frontend
```

### Port Conflicts?

If ports conflict with your existing apps:
- Backend uses port **8000**
- Frontend uses port **3001**

Ensure these ports are free on your server.

---

## 🎯 After Deployment

1. **Create admin user** via the frontend: https://careflowai.veraldabs.co.uk
2. **Configure OpenAI API key** in environment
3. **Set up email/SMS** for patient notifications (optional)
4. **Enable monitoring** (optional)
5. **Test all features** - Triage, Scheduling, Scribe, etc.

---

## 📞 Support

If you need help:
1. Check logs: `docker-compose -f logs -f --tail=100`
2. Restart services: `docker-compose restart`
3. View API docs: Visit https://api.careflowai.veraldabs.co.uk/docs

---

**Built for easy subdomain deployment! 🚀**
