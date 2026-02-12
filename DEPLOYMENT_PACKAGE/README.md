# ✅ CAREFLOW AI - DEPLOYMENT READY

## 📦 Complete Deployment Package for Your Agent

All files are ready for your agent to deploy to your web server!

---

## 🎯 What's Included

| File | Purpose |
|------|---------|
| **DEPLOY_TO_YOUR_SERVER.md** | Deployment guide for your specific server IP |
| **test-connection.sh** | Pre-deployment connection test script |
| **manual-deploy.sh** | Manual deployment script if automated has issues |

---

## 📤 Send These Files to Your Agent

### Option 1: ZIP Package (Recommended - Fastest)

```bash
# Send the deployment package folder to your agent
# Location: C:\Users\evera\careflow-ai\DEPLOYMENT_PACKAGE\
# Size: ~8.5 MB

# Your agent should:
# 1. Extract the ZIP file
# 2. Upload to your server: 77.68.64.45
# 3. Follow DEPLOY_TO_YOUR_SERVER.md instructions
```

---

### Option 2: Individual Files (If ZIP Too Large)

Send in this order:

1. `DEPLOY_TO_YOUR_SERVER.md` - **Read this first!** (Complete instructions)
2. `test-connection.sh` - **Run before deploying!** (Verify server access)
3. `manual-deploy.sh` - **Main deployment script**
4. `docker-compose.prod.yml` - **Docker configuration**
5. `nginx/careflow-ai.conf` - **Nginx reverse proxy**
6. `.env.subdomain.template` - **Environment template for your subdomain**

---

## 🚀 Quick Deployment Commands

### Pre-Deployment Test:
```bash
# Test SSH and Docker access BEFORE deploying:
ssh -o ConnectTimeout=10 root@77.68.64.45 "docker ps && echo 'Docker: OK' && echo 'SSH: OK'"
```

### Full Deployment (If Test Passes):
```bash
# Upload and deploy
scp -r DEPLOYMENT_PACKAGE root@77.68.64.45:/opt/
ssh root@77.68.64.45
cd /opt/DEPLOYMENT_PACKAGE
chmod +x manual-deploy.sh
sudo ./manual-deploy.sh
```

---

## 📋 Configuration Files for Your Domain

### Important: Replace These Values in ALL Files:

**Domain:** `careflowai.veraldabs.co.uk`

**Find & Replace in these files:**
- `nginx/careflow-ai.conf` → 3 occurrences
- `.env.subdomain.template` → 1 occurrence
- `docker-compose.prod.yml` → Uses environment variables
- `deploy.sh` & `manual-deploy.sh` → DOMAIN variable

**Your agent must use find/replace to change:**
- `YOUR-DOMAIN.CO.UK` → `veraldabs.co.uk`
- `YOUR-DOMAIN.COM` → `veraldabs.co.uk`

---

## 🌐 Service URLs After Deployment

| Service | URL |
|----------|-----|
| **Frontend** | https://careflowai.veraldabs.co.uk |
| **Backend API** | https://api.careflowai.veraldabs.co.uk |
| **API Docs** | https://api.careflowai.veraldabs.co.uk/docs |
| **Health** | https://api.careflowai.veraldabs.co.uk/health |

---

## ✅ Pre-Deployment Checklist

Give this checklist to your agent:

- [ ] **Run `test-connection.sh` first** to verify server access
- [ ] **Read `DEPLOY_TO_YOUR_SERVER.md`** completely
- [ ] **Find/replace `YOUR-DOMAIN.CO.UK`** with `veraldabs.co.uk` everywhere
- [ ] **Find/replace `YOUR-DOMAIN.COM`** with `veraldabs.co.uk` everywhere
- [ ] **Upload files** to your server via SFTP/FTP
- [ ] **Run deployment script** (`manual-deploy.sh`)
- [ ] **Verify DNS** points to: `77.68.64.45`
- [ ] **Test frontend** loads at: `https://careflowai.veraldabs.co.uk`
- [ ] **Test backend health** at: `https://api.careflowai.veraldabs.co.uk/health`

---

## 🎯 Your Agent's Workflow

### Step 1: Pre-Deployment Verification
```bash
# Your agent runs this BEFORE uploading anything:
ssh -o ConnectTimeout=10 root@77.68.64.45 "docker ps && echo 'Docker: OK' && echo 'Write: OK' && echo 'SSH: OK'"
```

### Step 2: Upload Deployment Package
```bash
# Your agent uploads and extracts:
scp -r DEPLOYMENT_PACKAGE root@77.68.64.45:/opt/
```

### Step 3: Run Deployment Script
```bash
# Your agent connects and runs:
ssh root@77.68.64.45
cd /opt/DEPLOYMENT_PACKAGE
chmod +x manual-deploy.sh
sudo ./manual-deploy.sh --domain=careflowai.veraldabs.co.uk
```

### Step 4: DNS Configuration
```bash
# You/Your agent updates DNS:
# Add CNAME: careflowai → 77.68.64.45
# Wait 10-30 minutes for DNS propagation
```

---

## 📞 Troubleshooting

### Server Connection Issues?

**Problem**: "Permission denied (publickey,password)"

**Solutions**:
1. Check SSH key is correct
2. Try: `ssh root@77.68.64.45` (without `-o` options first)
3. Verify SSH access in server control panel

### Application Not Starting?

**Problem**: Containers won't start

**Solutions**:
1. Check Docker logs: `docker-compose -f docker-compose.prod.yml logs`
2. Verify environment variables are set correctly
3. Check database is ready: `docker-compose exec backend pg_isready`

### Frontend Shows "502 Bad Gateway"?

**Solutions**:
1. Backend containers not started yet (wait 1-2 minutes)
2. Check Nginx is running: `sudo systemctl status nginx`
3. Verify backend is healthy: `curl https://api.careflowai.veraldabs.co.uk/health`

---

## 🎉 Success Criteria

Deployment is successful when:

- ✅ Frontend loads at https://careflowai.veraldabs.co.uk
- ✅ Backend health returns: `{"status":"healthy"}`
- ✅ API docs accessible at https://api.careflowai.veraldabs.co.uk/docs
- ✅ No errors in Docker logs

---

## 📞 Support

If issues persist after following the guide:

1. **Check Docker logs**: `docker-compose -f logs -f --tail=100 backend`
2. **Check Nginx logs**: `sudo tail -f /var/log/nginx/careflowai-app-error.log`
3. **Verify DNS**: `nslookup careflowai.veraldabs.co.uk`
4. **Restart services**: `docker-compose restart`

---

**🚀 Your CareFlow AI application is ready to deploy!**
