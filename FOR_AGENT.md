# 📦 CareFlow AI - Production Deployment Package

## 🎯 Ready to Send to Your Agent

This deployment package contains everything needed to deploy CareFlow AI on your domain.

---

## 📦 Package Contents

```
DEPLOYMENT_PACKAGE/
├── README.md                           # Complete deployment guide
├── QUICK_START.md                      # Quick start for your agent
├── deploy.sh                           # Automated deployment script (executable)
├── docker-compose.prod.yml              # Production Docker setup
├── .env.production.template             # Environment variables template
└── nginx/
    └── careflow-ai.conf          # Nginx reverse proxy config
```

---

## 🚀 How to Send to Your Agent

### Option 1: Zip and Upload (Recommended)

```bash
# Create deployment package
cd C:\Users\evera\careflow-ai
zip -r DEPLOYMENT_PACKAGE careflow-ai-deploy.zip

# Send to your agent
# Your agent can upload: careflow-ai-deploy.zip (8.5 MB)
```

**Your agent will:**
1. Extract the zip file
2. Review QUICK_START.md for instructions
3. Edit .env.production with your domain: `187.77.96.80`
4. Upload to VPS and run `./deploy.sh --domain=careflowAI.YOUR-DOMAIN.COM`

---

### Option 2: Send Individual Files

If your agent prefers individual files, send them in this order:

1. **QUICK_START.md** - Start here (contains all instructions)
2. **deploy.sh** - The deployment script
3. **docker-compose.prod.yml** - Production Docker configuration
4. **nginx/careflow-ai.conf** - Nginx configuration (search/replace `YOUR-DOMAIN.COM`)
5. **.env.production.template** - Environment template

---

## 📋 Configuration Checklist

Before sending to your agent, verify:

- [ ] All files in DEPLOYMENT_PACKAGE are present
- [ ] `deploy.sh` is executable (chmod +x)
- [ ] Domain information is correct (187.77.96.80)
- [ ] Your agent knows the SSH credentials for the VPS
- [ ] Your agent has access to the domain registrar

---

## 🔑 What Your Agent Needs to Configure

### Required Variables

```bash
# In .env.production or during deployment:
DOMAIN=careflowAI.YOUR-DOMAIN.COM
APP_URL=https://careflowAI.YOUR-DOMAIN.COM
API_URL=https://api.careflowAI.YOUR-DOMAIN.COM
```

### DNS Configuration Required

Add these records at your domain registrar:

| Type | Name | Value | Purpose |
|------|------|-------|---------|
| **CNAME** | `careflowAI` | Points to your VPS/domain |
| **A** | `www` (optional) | Main domain redirect |

### SSL Certificate Setup

**Free Option: Let's Encrypt**
```bash
sudo certbot --nginx -d careflowAI.YOUR-DOMAIN.COM
```

**Better Option: Cloudflare** (Free)
- Add domain to Cloudflare
- Set SSL to "Full" mode
- Enable automatic HTTPS rewrites

---

## 🎯 After Your Agent Receives This

### Step 1: Upload to VPS

```bash
scp -r DEPLOYMENT_PACKAGE root@YOUR-VPS-IP:/opt/
```

### Step 2: Extract and Deploy

```bash
ssh root@YOUR-VPS-IP
cd /opt/DEPLOYMENT_PACKAGE
unzip careflow-ai-deploy.zip
cd careflow-ai-deploy

# Configure environment
cp .env.production.template .env.production
nano .env.production
# Update DOMAIN=careflowAI.YOUR-DOMAIN.COM
# Add OPENAI_API_KEY=sk-...
# Save and exit

# Deploy
chmod +x deploy.sh
sudo ./deploy.sh --domain=careflowAI.YOUR-DOMAIN.COM
```

### Step 3: Verify Deployment

```bash
# Test frontend
curl -I https://careflowAI.YOUR-DOMAIN.COM

# Test backend API
curl https://api.careflowAI.YOUR-DOMAIN.COM/health
```

---

## 📞 Expected URLs After Deployment

| Service | URL |
|----------|-----|
| Frontend | https://careflowAI.YOUR-DOMAIN.COM |
| Backend API | https://api.careflowAI.YOUR-DOMAIN.COM |
| API Docs | https://api.careflowAI.YOUR-DOMAIN.COM/docs |
| Health | https://api.careflowAI.YOUR-DOMAIN.COM/health |

---

## ⏱️ Timeline Estimates

For your agent:

| Task | Time Estimate |
|------|--------------|
| Receive package | 5 minutes |
| Upload to VPS | 10 minutes |
| Extract files | 5 minutes |
| Configure environment | 10 minutes |
| Run deployment script | 20 minutes |
| Verify deployment | 10 minutes |
| **Total** | **~60 minutes** |

---

## 📞 Quick Reference: Find & Replace

Your agent should do these find/replace operations:

```bash
# In nginx configuration:
# Find: YOUR-DOMAIN.COM
# Replace with: your-actual-domain.com

# In .env.production:
# Find: careflowAI.YOUR-DOMAIN.COM
# Replace with: careflowAI.YOUR-ACTUAL-DOMAIN.COM

# In docker-compose.prod.yml:
# No replacements needed - uses variables from .env.production
```

---

## 🎉 Success Criteria

Deployment is successful when:

- [ ] Frontend loads at https://careflowAI.YOUR-DOMAIN.COM
- [ ] Backend API responds to /health
- [ ] API documentation accessible at /docs
- [ ] No errors in Docker logs
- [ ] Nginx proxy working correctly

---

## Need Support?

If your agent encounters issues:

1. **Check Docker logs**: `docker-compose -f docker-compose.prod.yml logs backend`
2. **Check Nginx logs**: `sudo tail -f /var/log/nginx/careflow-app-error.log`
3. **Verify DNS**: `nslookup careflowAI.YOUR-DOMAIN.COM`
4. **Verify SSL**: `openssl s_client -connect careflowAI.YOUR-DOMAIN.COM:443`
5. **Test locally**: `curl -v http://187.77.96.80/health`

---

**Built for easy deployment to: http://187.77.96.80/careflowAI**
