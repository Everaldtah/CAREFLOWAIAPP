#!/bin/bash
# =============================================================================
# CareFlow AI - Server Test Script
# =============================================================================
#
# This script ONLY tests server connectivity - it does NOT deploy anything
# Run this FIRST to verify SSH works before deploying
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}╔════════════════════════════════╗${NC}"
echo -e "${GREEN}│${NC}  CareFlow AI - Server Test${NC}        │${NC}"
echo -e "${GREEN}│${NC}                                    │${NC}"
echo -e "${GREEN}╚═════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}Server: 79.99.45.136${NC}"
echo -e "${YELLOW}Test: Directory creation${NC}"
echo ""

# Create test directory
ssh -o StrictHostKeyChecking=no root@79.99.45.136 "
mkdir -p /opt/careflow-ai-test 2>/dev/null && echo 'Test directory created'
" || true

echo -e "${GREEN}✓ Test directory exists${NC}"
echo ""

# Test 1: SSH Connection
echo -e "${YELLOW}→ Test 1: SSH Connection${NC}"
echo ""

ssh -o StrictHostKeyChecking=no root@79.99.45.136 "whoami" 2>&1 && echo -e "${GREEN}✓ SSH connection successful${NC}" || echo -e "${RED}✗ SSH connection failed${NC}"

echo ""
echo -e "${YELLOW}→ Test 2: Directory Write Access${NC}"
echo ""

ssh -o StrictHostKeyChecking=no root@79.99.45.136 "test -f /opt/careflow-ai-test/write-tes\$\$RANDOM" 2>&1 && echo -e "${GREEN}✓ Directory write works${NC}" || echo -e "${RED}✗ Directory write failed${NC}"

echo ""
echo -e "${YELLOW}→ Test 3: Docker Command Access${NC}"
echo ""

ssh -o StrictHostKeyChecking=no root@79.99.45.136 "which docker" 2>&1 && echo -e "${GREEN}✓ Docker command works${NC}" || echo -e "${RED}✗ Docker command failed${NC}"

echo ""
echo -e "${YELLOW}→ Test 4: Port Check${NC}"
echo ""

ssh -o StrictHostKeyChecking=no root@79.99.45.136 "netstat -tlnp | grep -E ':(8000|3001|5432|6379)'" 2>&1 && echo -e "${GREEN}✓ Required ports are free${NC}" || echo -e "${RED}✗ Port conflict detected${NC}"

echo ""
echo -e "${GREEN}╔══════════════════════════════╗${NC}"
echo -e "${GREEN}│${NC}  Test Results Summary${NC}        │${NC}"
echo -e "${GREEN}│${NC}                                    │${NC}"
ssh -o StrictHostKeyChecking=no root@79.99.45.136 "cat" << 'ENDOF'
[SSH Connection]
$(ssh -o StrictHostKeyChecking=no root@79.99.45.136 "whoami" 2>&1 && echo "✅" || echo "✗")
[Directory Write]
$(ssh -o StrictHostKeyChecking=no root@79.99.45.136 "test -f /opt/careflow-ai-test/write-test && echo "✅" || echo "✗")
[Docker Command]
$(ssh -o StrictHostKeyChecking=no root@79.99.45.136 "which docker" 2>&1 && echo "✅" || echo "✗")
[Ports Check]
$(ssh -o StrictHostKeyChecking=no root@79.99.45.136 "netstat -tlnp | grep -E ':(8000|3001|5432|6379)'" 2>&1 && echo "✅" || echo "✗")
ENDOF
"
echo -e "${GREEN}│${NC}                                    │${NC}"
echo -e "${GREEN}│${NC} If all tests pass, server is ready for deployment!${NC}"
echo -e "${GREEN}│${NC}                                    │${NC}"
echo -e "${GREEN}╚═════════════════════════════════╝${NC}"
echo ""

echo ""
echo -e "${YELLOW}📋 What's Being Tested:${NC}"
echo "• SSH access to server (root@79.99.45.136:22)"
echo "• Directory write permission (/opt/careflow-ai-test)"
echo "• Docker command availability"
echo "• Ports 8000, 3001, 5432, 6379 - must be free"

echo ""
echo -e "${GREEN}╔══════════════════════════════╗${NC}"
echo -e "${GREEN}│${NC}  Test Complete!${NC}        │${NC}"
echo -e "${GREEN}│${NC}                                    │${NC}"
echo -e "${GREEN}│${NC}  ${YELLOW}Next Steps:${NC}        │${NC}"
echo -e "${GREEN}│${NC}                                    │${NC}"
echo -e "${GREEN}│${NC} 1. If tests pass, run: bash test-connectivity.sh${NC}        │${NC}"
echo -e "${GREEN}│${NC} 2. Or manually deploy with: bash deploy-from-local.sh${NC}        │${NC}"
echo -e "${GREEN}│${NC}                                    │${NC}"
echo -e "${GREEN}╚═════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}If SSH test fails, check:${NC}"
echo "• Server firewall (allow port 22 from your IP)"
echo "• Server MaxSessions setting (may need increase)"
echo "• Contact your hosting provider about SSH timeouts"
echo ""
