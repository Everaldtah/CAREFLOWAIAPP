# CareFlow AI - VPS Deployment Guide

Complete guide to deploy CareFlow AI on your VPS for production.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Deploy (Automated)](#quick-deploy-automated)
3. [Manual Deploy](#manual-deploy)
4. [SSL Certificate Setup](#ssl-certificate-setup)
5. [Security Hardening](#security-hardening)
6. [Monitoring & Backups](#monitoring--backups)

---

## Prerequisites

### VPS Requirements
- **Minimum**: 2GB RAM, 1 CPU, 40GB SSD
- **Recommended**: 4GB RAM, 2 CPU, 80GB SSD
- **OS**: Ubuntu 22.04 LTS or Debian 12

### Before You Start
1. Point your domain to your VPS IP:
   - `A` record: `@` → `your-vps-ip`
   - `A` record: `api` → `your-vps-ip`

2. SSH into your VPS:
   ```bash
   ssh root@your-vps-ip
   ```

---

## Quick Deploy (Automated)

### Option 1: One-Line Setup

```bash
curl -fsSL https://raw.githubusercontent.com/your-repo/careflow-ai/main/deploy/vps-setup.sh | bash
```

### Option 2: Download and Run

```bash
# Download the script
wget https://raw.githubusercontent.com/your-repo/careflow-ai/main/deploy/vps-setup.sh

# Make executable
chmod +x vps-setup.sh

# Run with your domain
sudo DOMAIN=yourdomain.com ADMIN_EMAIL=you@email.com ./vps-setup.sh
```

**What this does:**
- ✅ Installs Docker & Docker Compose
- ✅ Installs Nginx reverse proxy
- ✅ Installs Fail2ban for security
- ✅ Creates directories and environment files
- ✅ Generates secure passwords and keys

---

## Manual Deploy

If you prefer manual setup or the script fails:

### Step 1: Install Docker

```bash
# Update system
apt-get update && apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl enable docker
systemctl start docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### Step 2: Upload Your Files

```bash
# On your local machine
scp -r careflow-ai root@your-vps-ip:/opt/

# Or use git (recommended)
git clone https://github.com/your-repo/careflow-ai.git /opt/careflow-ai
```

### Step 3: Configure Environment

```bash
cd /opt/careflow-ai
cp .env.example .env
nano .env  # Edit your settings
```

**Required variables to set:**
```bash
DOMAIN=yourdomain.com
API_URL=https://api.yourdomain.com
APP_URL=https://yourdomain.com
OPENAI_API_KEY=sk-...  # Get from platform.openai.com
```

### Step 4: Start Services

```bash
# Start production containers
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Step 5: Run Migrations

```bash
# Database migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Seed database (optional - creates demo data)
docker-compose -f docker-compose.prod.yml exec backend python scripts/seed_db.py
```

---

## SSL Certificate Setup

### Option 1: Let's Encrypt (Free, Recommended)

```bash
# Install Certbot
apt-get install -y certbot python3-certbot-nginx

# Get certificate for both domains
certbot --nginx -d yourdomain.com -d api.yourdomain.com

# Auto-renewal (already configured)
certbot renew --dry-run
```

### Option 2: Cloudflare (Free, Better)

1. **Create Cloudflare account** (cloudflare.com)
2. **Add your site** to Cloudflare
3. **Change nameservers** at your domain registrar
4. **Enable "Full SSL"** in Cloudflare SSL/TLS settings
5. **Set up Page Rules** (optional, for caching)

---

## Security Hardening

### 1. Firewall Setup

```bash
# Install UFW firewall
apt-get install -y ufw

# Default policies
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (IMPORTANT - before enabling!)
ufw allow 22/tcp

# Allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Enable firewall
ufw enable

# Check status
ufw status
```

### 2. Fail2ban (Already Installed)

```bash
# Enable fail2ban
systemctl enable fail2ban
systemctl start fail2ban

# Check status
fail2ban-client status
```

### 3. Secure SSH

```bash
# Edit SSH config
nano /etc/ssh/sshd_config

# Change these settings:
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes

# Restart SSH
systemctl restart sshd

# Create a non-root user
adduser careflow
usermod -aG docker careflow

# SSH key setup (on your local machine)
ssh-copy-id careflow@your-vps-ip
```

### 4. Database Security

The database is **not exposed to the internet** - it's on an internal Docker network. Only the backend container can access it.

---

## Monitoring & Backups

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend

# Nginx logs
tail -f /var/log/nginx/careflow-api-access.log
tail -f /var/log/nginx/careflow-frontend-access.log
```

### Database Backups

```bash
# Manual backup
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U careflow careflow_prod > backup_$(date +%Y%m%d).sql

# Automated backup (add to crontab)
0 2 * * * cd /opt/careflow-ai && docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U careflow careflow_prod > /backups/careflow_$(date +\%Y\%m\%d).sql
```

### Health Checks

```bash
# Backend health
curl https://api.yourdomain.com/health

# Frontend health
curl https://yourdomain.com
```

### Resource Monitoring

```bash
# Container stats
docker stats

# Disk usage
df -h

# Memory usage
free -h
```

---

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Restart specific service
docker-compose -f docker-compose.prod.yml restart backend

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build backend
```

### Database Connection Issues

```bash
# Check if postgres is running
docker-compose -f docker-compose.prod.yml ps postgres

# Check postgres logs
docker-compose -f docker-compose.prod.yml logs postgres

# Connect to database
docker-compose -f docker-compose.prod.yml exec postgres psql -U careflow -d careflow_prod
```

### SSL Certificate Issues

```bash
# Renew certificate
certbot renew

# Restart nginx
systemctl restart nginx
```

---

## Cost Summary

| Service | Cost (Monthly) |
|---------|----------------|
| VPS (2GB RAM) | $5-6 (Hetzner/Linode) |
| Domain | $1-2 (first year) |
| SSL Certificate | **FREE** (Let's Encrypt) |
| Cloudflare | **FREE** |
| **Total** | **~$6-8/month** |

---

## Post-Deployment Checklist

- [ ] Services are running (`docker ps`)
- [ ] SSL certificate is valid
- [ ] Database migrations completed
- [ ] Frontend loads at `https://yourdomain.com`
- [ ] API is accessible at `https://api.yourdomain.com`
- [ ] Health check returns OK
- [ ] Backups are configured
- [ ] Firewall is enabled
- [ ] Monitoring is set up
- [ ] Create admin user via API or frontend

---

## Need Help?

- Check logs: `docker-compose -f docker-compose.prod.yml logs -f`
- Check health: `curl https://api.yourdomain.com/health`
- GitHub Issues: [github.com/your-repo/careflow-ai/issues]

---

**Congratulations! Your CareFlow AI instance is now live! 🎉**
