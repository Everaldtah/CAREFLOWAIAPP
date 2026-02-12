#!/bin/bash
# CareFlow AI - VPS Deployment Script
# Run on your VPS: curl -sSL https://your-domain.com/deploy.sh | bash

set -e

echo "🏥 CareFlow AI - VPS Deployment"
echo "================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Variables
DOMAIN="${DOMAIN:-yourdomain.com}"
API_DOMAIN="api.${DOMAIN}"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@${DOMAIN}}"
DB_PASSWORD="${DB_PASSWORD:-$(openssl rand -base64 32)}"
SECRET_KEY="${SECRET_KEY:-$(openssl rand -hex 32)}"
ENCRYPTION_KEY="${ENCRYPTION_KEY:-$(openssl rand -base64 32)}"

echo "📋 Configuration:"
echo "   Domain: $DOMAIN"
echo "   API Domain: $API_DOMAIN"
echo ""

# 1. Update system
echo "📦 Updating system packages..."
apt-get update && apt-get upgrade -y

# 2. Install Docker
echo "🐳 Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl enable docker
    systemctl start docker
fi

# 3. Install Docker Compose
echo "🔧 Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# 4. Install Nginx
echo "🌐 Installing Nginx..."
apt-get install -y nginx certbot python3-certbot-nginx

# 5. Install Fail2ban (security)
echo "🔒 Installing Fail2ban..."
apt-get install -y fail2ban

# 6. Create directories
echo "📁 Creating directories..."
mkdir -p /opt/careflow-ai
mkdir -p /opt/careflow-ai/postgres/data
mkdir -p /opt/careflow-ai/redis/data
mkdir -p /var/www/certbot

# 7. Create .env file
echo "⚙️ Creating environment file..."
cat > /opt/careflow-ai/.env << EOF
# =============================================================================
# CareFlow AI - Production Environment
# =============================================================================

# Application
APP_NAME=CareFlow AI
APP_VERSION=1.0.0
APP_ENV=production
APP_DEBUG=false
APP_URL=https://${DOMAIN}
API_URL=https://${API_DOMAIN}

# Database (Internal Docker network)
DATABASE_URL=postgresql://careflow:${DB_PASSWORD}@postgres:5432/careflow_prod

# Redis (Internal Docker network)
REDIS_URL=redis://redis:6379/0
REDIS_CACHE_URL=redis://redis:6379/1
REDIS_AGENT_STATE_URL=redis://redis:6379/2

# Security
SECRET_KEY=${SECRET_KEY}
SECRET_KEY_REFRESH=${SECRET_KEY}_refresh
ENCRYPTION_KEY=${ENCRYPTION_KEY}

# AI Provider (Add your API key)
OPENAI_API_KEY=\${OPENAI_API_KEY:-}
ANTHROPIC_API_KEY=\${ANTHROPIC_API_KEY:-}

# CORS
CORS_ORIGINS=https://${DOMAIN},https://www.${DOMAIN}

# Email (Configure your SMTP)
SMTP_HOST=\${SMTP_HOST:-smtp.gmail.com}
SMTP_PORT=587
SMTP_USER=\${SMTP_USER:-}
SMTP_PASSWORD=\${SMTP_PASSWORD:-}
SMTP_FROM=noreply@${DOMAIN}
SMTP_FROM_NAME=CareFlow AI

# Compliance
COMPLIANCE_RETENTION_DAYS=2555
COMPLIANCE_AUDIT_LOG_RETENTION_DAYS=2555
COMPLIANCE_ANONYMIZE_AFTER_RETENTION=true

# Multi-tenancy
TENANT_ISOLATION_LEVEL=database
MAX_CLINICS_PER_TENANT=100
MAX_USERS_PER_CLINIC=500

# Frontend
NEXT_PUBLIC_APP_URL=https://${DOMAIN}
NEXT_PUBLIC_API_URL=https://${API_DOMAIN}
NEXT_PUBLIC_ENABLE_ANALYTICS=false

# Monitoring
SENTRY_DSN=\${SENTRY_DSN:-}
SENTRY_ENVIRONMENT=production

# Logging
LOG_LEVEL=INFO

# Backup
BACKUP_ENABLED=true
BACKUP_SCHEDULE="0 2 * * *"
BACKUP_RETENTION_DAYS=30

# Database (for docker-compose)
POSTGRES_DB=careflow_prod
POSTGRES_USER=careflow
POSTGRES_PASSWORD=${DB_PASSWORD}
EOF

chmod 600 /opt/careflow-ai/.env

# 8. Save credentials
echo "🔐 Saving credentials..."
cat > /opt/careflow-ai/credentials.txt << EOF
# CareFlow AI Credentials
# IMPORTANT: Save this file securely!

Database Password: ${DB_PASSWORD}
Secret Key: ${SECRET_KEY}
Encryption Key: ${ENCRYPTION_KEY}

Database: postgresql://careflow:${DB_PASSWORD}@postgres:5432/careflow_prod
EOF
chmod 600 /opt/careflow-ai/credentials.txt

echo "✅ Setup complete!"
echo ""
echo "📝 Next Steps:"
echo "   1. Upload your application files to /opt/careflow-ai"
echo "   2. Add your OPENAI_API_KEY to /opt/careflow-ai/.env"
echo "   3. Run: docker-compose -f /opt/careflow-ai/docker-compose.prod.yml up -d"
echo "   4. Configure SSL: certbot --nginx -d ${DOMAIN} -d ${API_DOMAIN}"
echo "   5. Run migrations: docker-compose -f /opt/careflow-ai/docker-compose.prod.yml exec backend alembic upgrade head"
echo ""
echo "📄 Credentials saved to: /opt/careflow-ai/credentials.txt"
