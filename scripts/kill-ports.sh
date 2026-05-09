#!/bin/bash
# CredsCore - Kill Services by Port (Bash/Git Bash)
# This script kills processes running on CredsCore service ports

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${RED}========================================${NC}"
echo -e "${RED} CredsCore - Stopping All Services${NC}"
echo -e "${RED}========================================${NC}"
echo ""

# Ports used by CredsCore services
ports=(3000 4000 8000 8001 8002 8003 8004 8005 8006 8007 8008 8009 8090 9092 6379)

killed_count=0

# Detect if running on Windows (Git Bash/MINGW)
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    IS_WINDOWS=true
else
    IS_WINDOWS=false
fi

for port in "${ports[@]}"; do
    if [ "$IS_WINDOWS" = true ]; then
        # Windows: use netstat to find PID
        pid=$(netstat -ano 2>/dev/null | grep ":$port " | grep LISTENING | awk '{print $NF}' | head -1)
        if [ -n "$pid" ]; then
            echo -e "${YELLOW}Stopping process on port $port (PID: $pid)...${NC}"
            taskkill /PID "$pid" /F 2>/dev/null
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✓ Killed process on port $port${NC}"
                ((killed_count++))
            fi
        fi
    else
        # Unix/Mac: use lsof
        pid=$(lsof -ti:$port 2>/dev/null)
        if [ -n "$pid" ]; then
            echo -e "${YELLOW}Stopping process on port $port (PID: $pid)...${NC}"
            kill -9 $pid 2>/dev/null
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✓ Killed process on port $port${NC}"
                ((killed_count++))
            fi
        fi
    fi
done

echo ""
if [ $killed_count -gt 0 ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN} Stopped $killed_count service(s)${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo -e "${YELLOW}No active services found on CredsCore ports.${NC}"
fi
echo ""
