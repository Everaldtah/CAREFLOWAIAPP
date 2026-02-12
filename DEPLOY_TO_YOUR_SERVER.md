# 🚀 Deploy CareFlow AI to Your Web Server
# =============================================================================

Your server IP: **77.68.64.45**

---

## 📋 Step 1: Upload Files to Your Server

### Option A: Upload Deployment Package

1. Download the deployment package:
   - File: `C:\Users\evera\careflow-ai\careflow-ai-deploy.zip` (8.5 MB)

2. Upload to your server using SFTP or file manager:
   ```
   # Location: /root/  or /home/
   scp -r C:\Users\evera\careflow-ai\careflow-ai-deploy.zip root@77.68.64.45:/opt/
   ```

### Option B: Upload Individual Files (If Package Too Large)

Upload in this order:
1. `docker-compose.prod.yml` → `/opt/careflow-ai/docker-compose.prod.yml`
2. `.env.production` → `/opt/careflow-ai/.env.production`
3. `nginx/careflow-ai.conf` → `/etc/nginx/sites-available/careflow-ai.conf`
4. Configure environment (see Step 2)

---

## 📋 Step 2: Configure Environment Variables

### Create `.env.production` file:

```bash
# SSH into your server
ssh root@77.68.64.45

# Create environment file
cat > /opt/careflow-ai/.env.production << 'EOF'
# =============================================================================
# CareFlow AI - Production Environment
# =============================================================================

# Domain configuration for SUBDOMAIN
DOMAIN=careflowai.veraldabs.co.uk
APP_URL=https://careflowai.veraldabs.co.uk
API_URL=https://api.careflowai.veraldabs.co.uk

# API Configuration for SUBDOMAIN
NEXT_PUBLIC_APP_URL=https://careflowai.veraldabs.co.uk
NEXT_PUBLIC_API_URL=https://api.careflowai.veraldabs.co.uk

# CORS Configuration for SUBDOMAIN
CORS_ORIGINS=https://careflowai.veraldabs.co.uk,https://www.veraldabs.co.uk

# =============================================================================
# Database Configuration
# =============================================================================

# PostgreSQL
DATABASE_URL=postgresql://careflow:YOUR_DB_PASSWORD@postgres:5432/careflow_prod

# Redis
REDIS_URL=redis://redis:6379/0

# =============================================================================
# Security (NEVER USE THESE IN PRODUCTION!)
# =============================================================================

# Generate secret keys with:
# python -c "import secrets; print(secrets.token_hex(32))"
# openssl rand -base64 32

SECRET_KEY=CHANGE-THIS-SECRET-KEY-IN-SUBDOMAIN-PRODUCTION-USE-OPENSSL-RAND-BASE64-32
SECRET_KEY_REFRESH=CHANGE-THIS-REFRESH-SECRET-KEY-IN-SUBDOMAIN-PRODUCTION

# AES-256 encryption key for PHI (32 bytes hex)
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
ENCRYPTION_KEY=CHANGE-THIS-ENCRYPTION-KEY-32-BYTES-HEX-EXACTLY-FOR-SUBDOMAIN-PRODUCTION

# =============================================================================
# AI Provider Configuration
# =============================================================================

# OpenAI API Key - Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-openai-api-key-here

# =============================================================================
# Email Configuration (Optional)
# =============================================================================

# SMTP Settings for sending emails
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@veraldabs.co.uk
SMTP_FROM_NAME=CareFlow AI

# =============================================================================
# Application Settings
# =============================================================================

APP_ENV=production
APP_DEBUG=false
APP_VERSION=1.0.0

# =============================================================================
# Monitoring & Logging
# =============================================================================

# Sentry DSN for error tracking (optional)
# SENTRY_DSN=
# SENTRY_ENVIRONMENT=production

# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# =============================================================================
# Frontend Configuration
# =============================================================================

NEXT_PUBLIC_ENABLE_ANALYTICS=true
EOF
```

---

## 📋 Step 3: Extract and Deploy

### Extract Deployment Package (If using ZIP):

```bash
# SSH into server
ssh root@77.68.64.45

# Extract package
cd /opt
unzip careflow-ai-deploy.zip
cd careflow-ai-deploy

# Deploy!
chmod +x deploy.sh
sudo ./deploy.sh --domain=careflowai.veraldabs.co.uk
```

### Or Upload Files Individually:

```bash
# 1. Upload docker-compose.prod.yml
scp docker-compose.prod.yml root@77.68.64.45:/opt/careflow-ai/docker-compose.prod.yml

# 2. Create .env.production
# (Use the content from Step 2 above)
cat > /opt/careflow-ai/.env.production
# Paste the environment variables...

# 3. Upload nginx config
scp nginx/careflow-ai.conf root@77.68.64.45:/etc/nginx/sites-available/

# 4. Restart nginx
sudo nginx -s reload

# 5. Start containers
cd /opt/careflow-ai
docker-compose -f docker-compose.prod.yml up -d --build

# 6. Run database migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 7. Check services
docker-compose -f docker-compose.prod.yml ps
```

---

## 🔍 Verify Deployment

After deployment, test these URLs:

```bash
# Test frontend
curl -I https://careflowai.veraldabs.co.uk

# Test backend health
curl https://api.careflowai.veraldabs.co.uk/health

# Test API documentation
# Open in browser: https://api.careflowai.veraldabs.co.uk/docs
```

**Expected Results:**
- ✅ Frontend returns 200 OK
- ✅ Backend health returns: `{"status":"healthy"}`
- ✅ API docs accessible

---

## 📊 Your DNS Configuration

Add these records at your domain registrar:

| Type | Name | Value |
|------|------|-------|
| **CNAME** | `careflowai` | `77.68.64.45` |
| **A** | `www` | `77.68.64.45` (optional) |

---

## ⚠️ Important Notes

1. **Database Password**: Change `YOUR_DB_PASSWORD` in `.env.production` to a strong password!
2. **OpenAI API Key**: Add your actual API key
3. **Secret Keys**: The generated keys in the script are secure - you can use them or replace
4. **SSL Certificate**: Run `sudo certbot --nginx -d careflowai.veraldabs.co.uk` after deployment for free SSL

---

## 🎯 After Deployment

1. **Create admin user** → Visit https://careflowai.veraldabs.co.uk
2. **Test all features** → Triage, Scheduling, Scribe, etc.
3. **Set up email/SMS** → For patient notifications
4. **Configure monitoring** → Optional but recommended

---

**Need Help?**

If something doesn't work:

1. Check Docker logs: `docker-compose -f /opt/careflow-ai/docker-compose.prod.yml logs backend`
2. Check Nginx logs: `sudo tail -f /var/log/nginx/careflowai-app-error.log`
3. Verify DNS: `nslookup careflowai.veraldabs.co.uk`

---

**Your CareFlow AI app will be live at:**
🌐 **https://careflowai.veraldabs.co.uk** 🚀
