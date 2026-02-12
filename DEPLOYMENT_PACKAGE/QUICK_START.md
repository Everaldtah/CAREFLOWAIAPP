# 🚀 Quick Start Guide for CareFlow AI

## For Your Agent: One-Page Configuration

If you want your existing website to stay on the main domain and redirect to CareFlow AI:

### Simple HTML Redirect Page

Add this to your existing website's root:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url=https://careflowAI.YOUR-DOMAIN.COM">
    <title>Redirecting...</title>
</head>
<body>
    <p>Launching CareFlow AI Platform...</p>
    <p><a href="https://careflowAI.YOUR-DOMAIN.COM">Click here if not redirected</a></p>
</body>
</html>
```

This will automatically redirect visitors to your CareFlow AI app.

---

## Or: Subdomain Setup (Recommended)

Configure your existing website to add a link to the app:

```html
<!-- Add to your landing page -->
<div style="padding: 20px; background: #f3f4f6; border-radius: 8px;">
    <h3>🏥 Launch CareFlow AI</h3>
    <p>
        <a href="https://careflowAI.YOUR-DOMAIN.COM"
           style="display: inline-block; padding: 12px 24px; background: #2563eb; color: white; border-radius: 8px; text-decoration: none;">
            Launch Healthcare Platform →
        </a>
    </p>
</div>
```

---

## What Your Agent Needs to Do

### Step 1: DNS Configuration

Add these records to your domain registrar:

| Type | Name | Value |
|------|------|-------|
| **CNAME** | `careflowAI` | `187.77.96.80` (your root domain) |
| **A** | `www` | `187.77.96.80` (optional, for www redirect) |

### Step 2: Upload & Deploy

1. **Upload the deployment package** to your server:
   ```bash
   scp -r DEPLOYMENT_PACKAGE/ root@YOUR-VPS-IP:/opt/
   ```

2. **SSH into your server**:
   ```bash
   ssh root@YOUR-VPS-IP
   cd /opt/DEPLOYMENT_PACKAGE
   ```

3. **Run the deployment script**:
   ```bash
   chmod +x deploy.sh
   sudo ./deploy.sh --domain=YOUR-DOMAIN.COM
   ```

### Step 3: Configure Environment

The deployment script will prompt you for:
- OpenAI API Key (get from platform.openai.com)
- Secret keys (will generate options)
- SMTP settings (optional)

### Step 4: SSL Certificate

**Option A: Let's Encrypt (Free)**
```bash
sudo certbot --nginx -d careflowAI.YOUR-DOMAIN.COM
```

**Option B: Cloudflare (Free, Better)**
1. Add domain to Cloudflare
2. Set nameservers to Cloudflare
3. Enable "Full SSL" mode
4. Enable "Automatic HTTPS Rewrites"

---

## 📋 Pre-Deployment Checklist

Give your agent this checklist:

- [ ] Domain DNS configured (CNAME: careflowAI → 187.77.96.80)
- [ ] Deployment files uploaded to VPS
- [ ] Environment variables configured
- [ ] SSL certificate installed
- [ ] Application deployed and running
- [ ] Health checks passing
- [ ] Frontend accessible at domain
- [ ] Backend API accessible at domain
- [ ] API documentation accessible

---

## 🔗 Service URLs After Deployment

| Service | URL |
|----------|-----|
| **Frontend** | https://careflowAI.YOUR-DOMAIN.COM |
| **Backend API** | https://api.careflowAI.YOUR-DOMAIN.COM |
| **API Docs** | https://api.careflowAI.YOUR-DOMAIN.COM/docs |
| **Health Check** | https://api.careflowAI.YOUR-DOMAIN.COM/health |

---

## ⚠️ Troubleshooting

**Backend not responding?**
```bash
# Check if running
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs backend -f
```

**Frontend not loading?**
```bash
# Check nginx status
sudo systemctl status nginx

# Restart nginx
sudo systemctl restart nginx
```

**DNS not propagating?**
- DNS changes can take 24-48 hours
- Check propagation: `nslookup careflowAI.YOUR-DOMAIN.COM`
- Verify at: https://dnschecker.org

---

**Need Help?**

1. Check logs: `sudo journalctl -u nginx -f`
2. Check database: `docker-compose exec backend pg_isready`
3. Health check: `curl https://api.careflowAI.YOUR-DOMAIN.COM/health`

---

**Your agent can complete the deployment in ~15 minutes!**
