# 🖥️ SIMPLIFIED MANUAL DEPLOYMENT GUIDE
# ================================================================================
#
# Use this guide if automated deployment is having issues
# Your agent can follow these steps manually
# ================================================================================

## Step 1: Upload Files

Your agent should upload these files to your server:

```
1. docker-compose.prod.yml       → /opt/careflow-ai/
2. .env.production           → /opt/careflow-ai/
3. nginx/careflowai.conf     → /etc/nginx/sites-available/
```

## Step 2: Create Environment File

```bash
# SSH into server
ssh root@187.77.96.45

# Create environment file
cat > /opt/careflow-ai/.env.production << 'ENDOF'
DOMAIN=careflowai.veraldabs.co.uk
APP_URL=https://careflowai.veraldabs.co.uk
API_URL=https://api.careflowai.veraldabs.co.uk
NEXT_PUBLIC_APP_URL=https://careflowai.veraldabs.co.uk
NEXT_PUBLIC_API_URL=https://api.careflowai.veraldabs.co.uk

# Generate secrets (RUN THESE COMMANDS)
SECRET_KEY=$(openssl rand -base64 32)
ENCRYPTION_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Database password
DB_PASSWORD=$(openssl rand -base64 24 | tr -d 'n' | head -c 24)

# OpenAI API Key - ADD YOURS
OPENAI_API_KEY=sk-proj-8mrWoySV-PNfD5BlFwTcqBLPy8PYI73jrKgNXzhuFxLKGvmD1KrhvtBEk0

ENDOF
```

## Step 3: Start Application

```bash
cd /opt/careflow-ai-deploy

# Stop any existing containers
docker-compose -f docker-compose.prod.yml down

# Start services
docker-compose -f docker-compose.prod.yml up -d --build

# Wait for health
sleep 30

# Check status
docker-compose -f docker-compose.prod.yml ps
```

## Step 4: Configure Nginx

```bash
# Copy nginx config
cp /opt/careflow-ai-deploy/nginx/careflow-ai.conf /etc/nginx/sites-available/

# Enable site
ln -sf /etc/nginx/sites-available/careflow-ai.conf /etc/nginx/sites-enabled/

# Test configuration
nginx -t

# Reload nginx
systemctl reload nginx
```

## Step 5: Run Database Migrations

```bash
docker-compose -f /opt/careflow-ai-deploy/docker-compose.prod.yml exec -T backend alembic upgrade head
```

## Step 6: Verify Deployment

```bash
# Test backend
curl https://api.careflowai.veraldabs.co.uk/health

# Test frontend
curl -I https://careflowai.veraldabs.co.uk

# Expected output:
# Backend: {"status":"healthy"}
# Frontend: 200 OK
```

## Troubleshooting

### Backend not healthy?

```bash
# Check logs
docker-compose -f /opt/careflow-ai-deploy/docker-compose.prod.yml logs backend

# Check database
docker-compose -f /opt/careflow-ai-deploy/docker-compose.prod.yml exec backend pg_isready
```

### Frontend not loading?

```bash
# Check nginx
sudo systemctl status nginx

# Check nginx error log
sudo tail -f /var/log/nginx/careflowai-app-error.log
```

### Port conflicts?

```bash
# Check what's using ports
netstat -tlnp | grep -E ':(8000|3001|5432|6379|5050)'
```

---

**Your CareFlow AI app will be live at:**
🌐 https://careflowai.veraldabs.co.uk
