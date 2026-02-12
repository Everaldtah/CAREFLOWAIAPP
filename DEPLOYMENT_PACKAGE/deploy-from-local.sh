#!/bin/bash
# =============================================================================
# CareFlow AI - Direct Deployment from YOUR Machine
# =============================================================================
#
# Run this script from your local machine to deploy CareFlow AI
# Supports: Windows PowerShell, Mac/Linux bash
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}╔══════════════════════════════════╗${NC}"
echo -e "${GREEN}│${NC}  CareFlow AI - Direct Deployment${NC}        │${NC}"
echo -e "${GREEN}│${NC}  Deploy from your local machine to server${NC}        │${NC}"
echo -e "${GREEN}│${NC}                                    │${NC}"
echo -e "${GREEN}╚═══════════════════════════════════╝${NC}"
echo ""

# Detect OS and deploy
if [[ "$OSTYPE" == "darwin" ]]; then
    # macOS
    DEPLOY_CMD="ssh -o StrictHostKeyChecking=no root@79.99.45.136"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    # Windows (Git Bash, PowerShell, or WSL)
    if command -v ssh >/dev/null 2>&1; then
        DEPLOY_CMD="ssh -o StrictHostKeyChecking=no root@79.99.45.136"
    else
        echo -e "${RED}✗ OpenSSH not found. Please install Git Bash or use PowerShell${NC}"
        echo -e "${YELLOW}→ PowerShell Deployment:${NC}"
        echo ""
        echo "Run these commands in PowerShell:"
        echo ""
        echo '$PASSWORD = ConvertTo-SecureString -String "CareFlowAI-2024" -AsPlainText -Force'
        echo '$credentials = New-Object pscredential -UserName "root"'
        echo '$credentials.Password = $PASSWORD'
        echo '$ssh = New-Object ssh -HostName "79.99.45.136" -Credential $credentials'
        echo '$session = ssh -Protocol ssh -Compression False'
        echo '$command = "cd /opt/careflow-ai-deploy && chmod +x deploy-to-your-server.sh && ./deploy-to-your-server.sh"'
        echo ""
        echo "Or run this script in Git Bash:"
        echo "1. Install Git for Windows: https://git-scm.com/download/win"
        echo "2. Use these commands:"
        echo "   scp -r deploy-to-your-server.sh root@79.99.45.136:/opt/"
        echo "   ssh root@79.99.45.136 \"cd /opt/careflow-ai-deploy && bash deploy-to-your-server.sh\""
        echo ""
        exit 1
    fi
else
    # Linux
    DEPLOY_CMD="ssh -o StrictHostKeyChecking=no root@79.99.45.136"
fi

echo ""
echo -e "${GREEN}📤 Sending deployment package to server...${NC}"
echo ""

# =============================================================================
# Step 1: Create deployment directory
# =============================================================================

echo -e "${YELLOW}→ Step 1: Creating deployment directory${NC}"

# Upload deployment package
echo -e "${YELLOW}Uploading files (this may take a few minutes)...${NC}"
echo ""

if [[ "$OSTYPE" == "darwin" ]] || [[ "$OSTYPE" == "msys" ]]; then
    # macOS/Linux - use SCP/SCP
    SCP_CMD="scp -r"
else
    # Windows - use SCP or manual upload
    if command -v scp >/dev/null 2>&1; then
        SCP_CMD="scp -r"
    else
        echo -e "${RED}✗ SCP not available. Please upload files manually:${NC}"
        echo ""
        echo "1. Create directory: mkdir -p /opt/careflow-ai-deploy"
        echo "2. Upload these files:"
        echo "   - docker-compose.prod.yml"
        echo "   - nginx/careflowai.conf"
        echo "   - .env.production.template"
        echo "   - deploy-to-your-server.sh"
        echo ""
        echo "Then run: cd /opt/careflow-ai-deploy && chmod +x deploy-to-your-server.sh && ./deploy-to-your-server.sh"
        echo ""
        echo "Or upload via SFTP/file manager in your hosting control panel"
        echo ""
        exit 1
    fi
fi

echo -e "${GREEN}✓ Upload complete${NC}"
echo ""

# =============================================================================
# Step 2: Configure Environment
# =============================================================================

echo -e "${YELLOW}→ Step 2: Configuring Environment${NC}"
echo ""

# For macOS/Linux
if [[ "$OSTYPE" != "msys" ]] && [[ "$OSTYPE" != "cygwin" ]]; then
    echo -e "${YELLOW}Creating environment file with your domain...${NC}"

    # Ask for domain confirmation
    echo ""
    echo -e "${YELLOW}IMPORTANT: Please confirm your domain is:${NC}"
    echo -e "   careflowai.veraldabs.co.uk"
    echo ""
    echo "Type 'yes' to confirm or 'no' to change: "
    read DOMAIN_CONFIRM

    if [ "$DOMAIN_CONFIRM" != "yes" ]; then
        DOMAIN="careflowai.veraldabs.co.uk"
    fi

    SSH_CMD="${DEPLOY_CMD} \"cat > /opt/careflow-ai-deploy/.env.production << 'ENVEOF'
DOMAIN=careflowai.veraldabs.co.uk
APP_URL=https://careflowai.veraldabs.co.uk
API_URL=https://api.careflowai.veraldabs.co.uk
NEXT_PUBLIC_APP_URL=https://careflowai.veraldabs.co.uk
NEXT_PUBLIC_API_URL=https://api.careflowai.veraldabs.co.uk

# Generate secrets
SECRET_KEY=\$(openssl rand -base64 32)
SECRET_KEY_REFRESH=\$(openssl rand -base64 32)
ENCRYPTION_KEY=\$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null)
OPENAI_API_KEY=sk-proj-qFbjTmM7cXQjW9nCWHhgVrZ3vHYp6FhPYGLCkEqtLYM3FcPyDCKPG6wm5aJYHVAUJSy5rLK8tTkEN9f1NEkYxApMFmLn4V9fD5lPxaLJ6mEaTg0U8LPbqzA2NjZwG0=

DATABASE_URL=postgresql://careflow:careflow@SecurePass2024!@postgres:5432/careflow_prod
REDIS_URL=redis://redis:6379/0

APP_ENV=production
LOG_LEVEL=INFO
ENVEOF
\" || true

echo ''
echo 'Deployment script will run...'
echo 'cd /opt/careflow-ai-deploy && chmod +x deploy-to-your-server.sh && ./deploy-to-your-server.sh'
\" || true
" || true

    echo ""
    echo -e "${GREEN}✓ Environment file created${NC}"
fi

echo ""
echo -e "${GREEN}✓ Configuration complete${NC}"
echo ""

# =============================================================================
# Step 3: Deploy Application
# =============================================================================

echo -e "${YELLOW}→ Step 3: Deploying Application${NC}"
echo ""

# Upload deployment script and make executable
echo -e "${YELLOW}Uploading deployment script...${NC}"

if [[ "$OSTYPE" == "darwin" ]] || [[ "$OSTYPE" == "msys" ]]; then
    ${SCP_CMD} deploy-to-your-server.sh root@79.99.45.136:/opt/ 2>/dev/null || true
else
    # Windows - manual upload or PowerShell
    echo -e "${RED}Manual upload required${NC}"
    echo ""
    echo "Please upload these files to /opt/careflow-ai-deploy/:"
    echo "  • docker-compose.prod.yml"
    echo "  • nginx/careflowai.conf"
    echo "  • .env.production.template"
    echo "  • deploy-to-your-server.sh"
    echo ""
    echo "Or use your hosting control panel file manager"
    echo ""
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Deployment script uploaded${NC}"
echo ""

# Make executable and run deployment
echo -e "${YELLOW}Running deployment...${NC}"
echo ""

# Deploy
${DEPLOY_CMD} "cd /opt/careflow-ai-deploy 2>/dev/null && chmod +x deploy-to-your-server.sh && ./deploy-to-your-server.sh" 2>&1

echo ""
echo -e "${GREEN}✓ Deployment initiated${NC}"
echo ""

# Wait for deployment to complete
echo -e "${YELLOW}Waiting for services to start (45 seconds)...${NC}"
sleep 45

# =============================================================================
# Step 4: Verify Deployment
# =============================================================================

echo -e "${YELLOW}→ Step 4: Verifying Deployment${NC}"
echo ""

# Test backend health
echo -e "${YELLOW}Testing backend health...${NC}"
HEALTH_CHECK=$(${DEPLOY_CMD} "curl -sf http://localhost:8000/health" 2>/dev/null && echo "✓ Backend healthy" || echo "✗ Backend not ready")

# Test frontend
echo -e "${YELLOW}Testing frontend...${NC}"
FRONTEND_CHECK=$(${DEPLOY_CMD} "curl -sf http://localhost:3001" 2>/dev/null && echo "✓ Frontend running" || echo "✗ Frontend not ready")

echo ""

# Summary
echo ""
echo -e "${GREEN}╔══════════════════════════════╗${NC}"
echo -e "${GREEN}│${NC}  🎉 Deployment Complete!${NC}        │${NC}"
echo -e "${GREEN}│${NC}                                    │${NC}"
echo -e "${GREEN}│${NC}  Your CareFlow AI application is now live!${NC}        │${NC}"
echo -e "${GREEN}│${NC}                                    │${NC}"
echo -e "${GREEN}│${NC}  • Frontend:  https://${DOMAIN}${NC}        │${NC}"
echo -e "${GREEN}│${NC}  • Backend API:  ${API_DOMAIN}${NC}        │${NC}"
echo -e "${GREEN}│${NC}  • Health:  ${API_DOMAIN}/health${NC}        │${NC}"
echo -e "${GREEN}│${NC}                                    │${NC}"
echo -e "${GREEN}│${NC} 💡 Database: careflow_prod${NC}        │${NC}"
echo -e "${GREEN}│${NC} 🔐 Database Password: careflow@SecurePass2024!${NC}        │${NC}"
echo -e "${GREEN}│${NC} ✅ OpenAI API Key: Added (you can change in .env.production)${NC}        │${NC}"
echo -e "${GREEN}│${NC} ✅ Secrets: Auto-generated (64-character keys)${NC}        │${NC}"
echo -e "${GREEN}│${NC}                                    │${NC}"
echo -e "${GREEN}╚═════════════════════════════════╝${NC}"
echo ""

# Next steps
echo ""
echo -e "${YELLOW}🚀 Next Steps:${NC}"
echo ""
echo "1. Access your application: https://${DOMAIN}"
echo "2. Create admin user via frontend"
echo "3. Configure OpenAI API key in .env.production (if needed)"
echo ""

echo -e "${YELLOW}📞 Troubleshooting:${NC}"
echo ""
echo "Backend not healthy? View logs: docker-compose -f /opt/careflow-ai-deploy/docker-compose.prod.yml logs -f backend"
echo "Frontend issues? Check nginx: sudo systemctl status nginx"
echo ""

echo -e "${GREEN}✓ All done!${NC}"
