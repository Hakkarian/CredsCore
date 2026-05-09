#!/bin/bash
# Restart all CredsCore services

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m'

echo -e "${CYAN}=========================================="
echo -e " CredsCore - Restart All Services"
echo -e "==========================================${NC}"
echo ""

# Step 1: Kill existing processes
echo -e "${YELLOW}Step 1: Killing existing processes...${NC}"
cd "$SCRIPT_DIR"
bash "$SCRIPT_DIR/kill-ports.sh" 2>/dev/null || true

# Also kill any orphaned Python processes on our ports
for port in 3000 4000 8000 8001 8002 8003 8004 8005 8006 8007 8008 8009; do
    pid=$(netstat -ano 2>/dev/null | grep ":$port " | grep LISTENING | awk '{print $NF}' | head -1)
    if [ -n "$pid" ]; then
        taskkill /PID "$pid" /F 2>/dev/null || true
    fi
done

echo ""
echo -e "${GREEN}Processes killed.${NC}"
echo ""

# Step 2: Start services
echo -e "${YELLOW}Step 2: Starting all services...${NC}"
echo ""

cd "$SCRIPT_DIR"
bash "$SCRIPT_DIR/start-services-bg.sh"
