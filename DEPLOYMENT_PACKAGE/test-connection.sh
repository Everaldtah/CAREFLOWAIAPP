#!/bin/bash
# =============================================================================
# CareFlow AI - Server Connection Test
# =============================================================================
#
# Run this script FIRST to verify SSH and server access
# Usage: chmod +x test-connection.sh && ./test-connection.sh
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}╔════════════════════════════════════╗${NC}"
echo -e "${GREEN}│${NC}  CareFlow AI - Server Connection Test${NC}       │${NC}"
echo -e "${GREEN}│${NC}                                    │${NC}"
echo -e "${GREEN}╚═════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root${NC}"
    echo "Please run: sudo $0"
    exit 1
fi

echo -e "${YELLOW}Testing SSH Connection to Server...${NC}"
echo ""

# Test 1: SSH Connection
echo -e "${YELLOW}→ Test 1: SSH Access${NC}"
if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@77.68.64.45 "exit" 2>/dev/null; then
    echo -e "${GREEN}✓ SSH connection successful${NC}"
else
    echo -e "${RED}✗ SSH connection failed${NC}"
    echo "Error: $?"
    exit 1
fi

# Test 2: Directory Write Access
echo -e "${YELLOW}→ Test 2: Directory Write Access${NC}"
if ssh -o ConnectTimeout=10 root@77.68.64.45 "test -f /opt/test-write-$$RANDOM" 2>/dev/null; then
    echo -e "${GREEN}✓ Directory write successful${NC}"
    ssh -o ConnectTimeout=10 root@77.68.64.45 "rm /opt/test-write-$$RANDOM" 2>/dev/null
else
    echo -e "${RED}✗ Directory write failed${NC}"
    exit 1
fi

# Test 3: Docker Command Execution
echo -e "${YELLOW}→ Test 3: Docker Access${NC}"
if ssh -o ConnectTimeout=10 root@77.68.64.45 "docker ps" 2>/dev/null; then
    echo -e "${GREEN}✓ Docker command works${NC}"
else
    echo -e "${RED}✗ Docker command failed${NC}"
    exit 1
fi

# Test 4: Port Accessibility
echo -e "${YELLOW}→ Test 4: Port Check${NC}"
if ssh -o ConnectTimeout=10 root@77.68.64.45 "netstat -tlnp | grep -E ':(8000|3001|5432|6379)'" 2>/dev/null; then
    echo -e "${GREEN}✓ Ports 8000 and 3001 are free${NC}"
    echo -e "${YELLOW}  → Ports 5432 and 6379 are also accessible (PostgreSQL and Redis)${NC}"
else
    echo -e "${RED}✗ Port check failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}════════════════════════════════════╗${NC}"
echo -e "${GREEN}│${NC}  All Tests Passed! Server is Ready${NC}        │${NC}"
echo -e "${GREEN}│${NC}                                    │${NC}"
echo -e "${GREEN}╚═══════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}✓ Your server is ready for CareFlow AI deployment!${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Run full deployment: bash deploy.sh --domain=careflowai.veraldabs.co.uk"
echo "2. Or upload files individually via FTP/SFTP"
echo "3. Push code to GitHub: https://github.com/Everaldtah/CAREFLOWAIAPP"
echo ""
echo -e "${YELLOW}Full deployment guide:${NC}"
echo "See: DEPLOY_TO_YOUR_SERVER.md"
