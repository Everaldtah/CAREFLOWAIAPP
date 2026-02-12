#!/bin/bash
# =============================================================================
# CareFlow AI - Production Deployment for Subdomains
# =============================================================================
#
# Enhanced deployment script that supports both main domains and subdomains
# Example: careflowai.yourdomain.com or careflowai.yourdomain.co.uk
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}│${NC} CareFlow AI - Subdomain Deployment${NC}        │${NC}"
echo -e "${GREEN}╚═════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}✗ Error: This script must be run as root${NC}"
    echo "Please run: sudo $0"
    exit 1
fi

# =============================================================================
# Configuration
# =============================================================================

DEPLOY_DIR="/opt/careflow-ai"
ENV_FILE=".env.production"
SUBDOMAIN_ENV_FILE=".env.subdomain"

# Detect if subdomain deployment
IS_SUBDOMAIN=false

# Configuration
echo -e "${YELLOW}⚙ Configuration${NC}"
echo "Deploy directory: ${DEPLOY_DIR}"
echo "Main env file: ${ENV_FILE}"
echo "Subdomain env file: ${SUBDOMAIN_ENV_FILE} (for subdomains)"
echo ""

# Parse command line arguments
DOMAIN_NAME=""
SKIP_MIGRATIONS=false
USE_SUBDOMAIN_TEMPLATE=false
FORCE_SUBDOMAIN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --domain=*)
            DOMAIN_NAME="${1#*=}"
            USE_SUBDOMAIN_TEMPLATE=false
            FORCE_SUBDOMAIN=false
            ;;
        --subdomain)
            IS_SUBDOMAIN=true
            USE_SUBDOMAIN_TEMPLATE=true
            FORCE_SUBDOMAIN=true
            ;;
        --use-subdomain-template)
            USE_SUBDOMAIN_TEMPLATE=true
            FORCE_SUBDOMAIN=true
            ;;
        --skip-migrations)
            SKIP_MIGRATIONS=true
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Deploys CareFlow AI with support for subdomains"
            echo ""
            echo "Options:"
            echo "  --domain=NAME          Set main domain name (default: careflowAI)"
            echo "  --subdomain=NAME       Set subdomain name (e.g., careflowai for careflowai.yourdomain.com)"
            echo "  --use-subdomain-template  Use subdomain template (.env.subdomain.template)"
            echo "  --skip-migrations      Skip database migrations"
            echo "  --help                Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
    shift
done

# =============================================================================
# Domain Configuration
# =============================================================================

# Determine which environment file to use
if [ "$IS_SUBDOMAIN" = true ]; then
    ENV_FILE_TO_USE="$SUBDOMAIN_ENV_FILE"
    echo -e "${YELLOW}→ Subdomain Mode: Using .env.subdomain.template${NC}"
else
    ENV_FILE_TO_USE="$ENV_FILE"
    echo -e "→ Main Domain Mode: Using .env.production.template${NC}"
fi

# Set default domain
if [ -z "$DOMAIN_NAME" ]; then
    if [ "$IS_SUBDOMAIN" = true ]; then
        DOMAIN_NAME="careflowai"  # Default subdomain name
        FULL_DOMAIN="YOUR-DOMAIN.CO.UK"  # Default TLD for subdomains
    else
        DOMAIN_NAME="careflowAI"  # Default main domain name
        FULL_DOMAIN="YOUR-DOMAIN.COM"  # Default TLD for main domain
    USE_SUBDOMAIN_TEMPLATE=false
fi

# Build full domain names
if [ "$USE_SUBDOMAIN_TEMPLATE" = true ] || [ "$IS_SUBDOMAIN" = true ]; then
    SUBDOMAIN="${DOMAIN_NAME}.${FULL_DOMAIN#*}"
else
    SUBDOMAIN="${DOMAIN_NAME}.${FULL_DOMAIN}"
fi

APP_DOMAIN="${SUBDOMAIN}"
API_DOMAIN="api.${SUBDOMAIN}"

echo -e "${GREEN}✓ Domain configured:${NC}  ${APP_DOMAIN}"
echo ""

# =============================================================================
# Step 1: Prepare Environment
# =============================================================================

echo -e "${YELLOW}→ Step 1: Environment Setup${NC}"

# Check which template to use
if [ -f "${ENV_FILE_TO_USE}" ] && [ ! -f "${ENV_FILE_TO_USE}.setup_required" ]; then
    ENV_TEMPLATE="${ENV_FILE_TO_USE}.template"
else
    ENV_TEMPLATE="${ENV_FILE_TO_USE}"
fi

if [ ! -f "${ENV_TEMPLATE}" ]; then
    echo -e "${RED}✗ Error: Environment template not found: ${ENV_TEMPLATE}${NC}"
    echo "Looking for: ${ENV_TEMPLATE}"
    exit 1
fi

# Copy environment template
echo -e "Creating ${ENV_FILE} from template..."
cp "${ENV_TEMPLATE}" "${ENV_FILE}"

# Mark as needing configuration
touch "${ENV_FILE}.setup_required"

echo ""
echo -e "${RED}⚠ IMPORTANT: Edit ${ENV_FILE} with your values!${NC}"
echo ""
echo "Required changes:"
echo " • DOMAIN=${APP_DOMAIN}"
echo " • APP_URL=https://${APP_DOMAIN}"
echo " • API_URL=https://${API_DOMAIN}"
echo " • Add your OPENAI_API_KEY"
echo " • Generate SECRET_KEY, ENCRYPTION_KEY (or use placeholders for testing)"
echo ""
echo "Additional subdomain-specific settings (if using subdomain):"
echo " • CORS_ORIGINS=https://${APP_DOMAIN},https://www.${APP_DOMAIN}"
echo ""
echo "Press Enter to continue when ready..."
read

# =============================================================================
# Step 2: Deploy Application
# =============================================================================

echo -e "${YELLOW}→ Step 2: Deploying Containers${NC}"

# Stop any existing containers
echo "Stopping existing containers..."
docker-compose -f "${DEPLOY_DIR}/docker-compose.prod.yml" down 2>/dev/null || true

# Pull latest images
echo "Pulling latest Docker images..."
docker-compose -f "${DEPLOY_DIR}/docker-compose.prod.yml" pull

# Build and start
echo "Building and starting production containers..."
docker-compose -f "${DEPLOY_DIR}/docker-compose.prod.yml" up -d --build

# Wait for services to be healthy
echo "Waiting for services to be healthy..."
sleep 30

# Check service status
echo ""
echo -e "${GREEN}Service Status:${NC}"
docker-compose -f "${DEPLOY_DIR}/docker-compose.prod.yml" ps

# =============================================================================
# Step 3: Database Migrations
# =============================================================================

if [ "$SKIP_MIGRATIONS" = false ]; then
    echo -e "${YELLOW}→ Step 3: Running Database Migrations${NC}"

    # Wait for backend to be ready
    echo "Waiting for backend to be ready..."
    sleep 20

    # Run migrations
    docker-compose -f "${DEPLOY_DIR}/docker-compose.prod.yml" exec -T backend alembic upgrade head

    echo -e "${GREEN}✓ Migrations completed${NC}"
else
    echo -e "${YELLOW}⊗ Skipping migrations (--skip-migrations flag set)${NC}"
fi

# =============================================================================
# Step 4: Configure Nginx (Optional)
# =============================================================================

echo -e "${YELLOW}→ Step 4: Nginx Configuration${NC}"

# Check if Nginx is available
if command -v nginx &> /dev/null; then
    echo -e "${GREEN}✓ Nginx detected${NC}"

    # Copy nginx config
    echo "Installing Nginx configuration..."
    cp "${DEPLOY_DIR}/nginx/careflow-ai.conf" /etc/nginx/sites-available/

    # Enable site
    ln -sf /etc/nginx/sites-available/careflow-ai.conf /etc/nginx/sites-enabled/ 2>/dev/null

    # Test and reload nginx
    echo "Testing Nginx configuration..."
    nginx -t
    systemctl reload nginx

    echo -e "${GREEN}✓ Nginx configured${NC}"
else
    echo -e "${YELLOW}⊗ Nginx not found - skipping${NC}"
    echo "Your web server already handles reverse proxy"
fi

# =============================================================================
# Step 5: Health Checks
# =============================================================================

echo -e "${YELLOW}→ Step 5: Verifying Deployment${NC}"

echo "Waiting for services to fully start..."
sleep 10

# Check backend health
echo "Checking backend health..."
if curl -sf http://localhost:8000/health 2>/dev/null; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
fi

# Check frontend
echo "Checking frontend..."
if curl -sf http://localhost:3001 2>/dev/null; then
    echo -e "${GREEN}✓ Frontend is running${NC}"
else
    echo -e "${RED}✗ Frontend not responding${NC}"
fi

# =============================================================================
# Final Summary
# =============================================================================

echo ""
echo -e "${GREEN}╔══════════════════════════════════════╗${NC}"
echo -e "${GREEN}│${NC} Deployment Complete!${NC}        │${NC}"
echo -e "${GREEN}│${NC}                                    │${NC}"
echo -e "${GREEN}│${NC} CareFlow AI is deployed at:${NC}        │${NC}"
echo -e "${GREEN}│${NC}                                    │${NC}"
echo -e "${GREEN}│${NC}  • Frontend: https://${APP_DOMAIN}${NC}        │${NC}"
echo -e "${GREEN}│${NC}  • Backend API: https://${API_DOMAIN}${NC}        │${NC}"
echo -e "${GREEN}│${NC}  • API Docs: https://${API_DOMAIN}/docs${NC}        │${NC}"
echo -e "${GREEN}│${NC}                                    │${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}📍 Service URLs:${NC}"
echo "   Frontend:  https://${APP_DOMAIN}"
echo "   Backend API:  https://${API_DOMAIN}"
echo "   API Docs:  https://${API_DOMAIN}/docs"
echo "   Health Check:  https://${API_DOMAIN}/health"
echo ""

# Mark environment as configured
if [ -f "${ENV_FILE}.setup_required" ]; then
    rm "${ENV_FILE}.setup_required"
fi

# Create .configured flag
touch "${ENV_FILE}.configured"

echo ""
echo -e "${YELLOW}🎉 Deployment Successful!${NC}"
echo ""
echo -e "${YELLOW}→ Next Steps for Your Agent:${NC}"
echo "1. Create admin user via frontend: https://${APP_DOMAIN}"
echo "2. Test all features: Triage, Scheduling, etc."
echo "3. Configure your OpenAI API key in ${ENV_FILE}"
echo ""
echo "For issues or questions, check the logs:"
echo "  • Backend: docker-compose -f ${DEPLOY_DIR}/docker-compose.prod.yml logs -f backend"
echo "  • Frontend: docker-compose -f ${DEPLOY_DIR}/docker-compose.prod.yml logs -f frontend"
echo "  • Nginx: sudo journalctl -u nginx -f"
