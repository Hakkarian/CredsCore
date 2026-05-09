#!/bin/bash
# Start all CredsCore services

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

echo -e "${CYAN}=========================================="
echo -e "  CredsCore - Starting All Services"
echo -e "==========================================${NC}"
echo ""

SERVICES=(
    "Credit Scoring:8001:start-credit-scoring.sh"
    "Fraud Detection:8002:start-fraud.sh"
    "Orchestrator:8003:start-orchestrator.sh"
    "Data Enrichment:8004:start-enrichment.sh"
    "Policy Engine:8005:start-policy.sh"
    "Report Generator:8006:start-reports.sh"
    "Synthetic Data:8007:start-synthetic-data.sh"
    "Augmented Scoring:8008:start-augmented-scoring.sh"
    "API Gateway:8000:start-gateway.sh"
)

echo -e "${YELLOW}Step 1: Killing any existing processes on ports...${NC}"
"$SCRIPT_DIR/kill-ports.sh" 2>/dev/null || true

echo ""
echo -e "${YELLOW}Step 2: Starting services...${NC}"
echo ""

PIDS=()
for svc in "${SERVICES[@]}"; do
    IFS=':' read -r name port script <<< "$svc"
    echo -e "  Starting ${GREEN}$name${NC} on port $port..."

    cd "$SCRIPT_DIR"
    bash "$script" > /tmp/creds_${port}.log 2>&1 &
    PIDS+=($!)

    sleep 0.5
done

echo ""
echo -e "${YELLOW}Step 3: Waiting for services to initialize...${NC}"
sleep 5

echo ""
echo -e "${CYAN}Service Status:${NC}"
echo "------------------------------------------"
for svc in "${SERVICES[@]}"; do
    IFS=':' read -r name port script <<< "$svc"
    if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
        echo -e "  $name (port $port): ${GREEN}Running${NC}"
    else
        echo -e "  $name (port $port): ${YELLOW}Starting...${NC}"
    fi
done

echo ""
echo -e "${YELLOW}Step 4: Starting Next.js client...${NC}"
cd "$PROJECT_ROOT/client"
npm run dev > /tmp/creds_client.log 2>&1 &
CLIENT_PID=$!

sleep 3

echo ""
echo -e "${CYAN}=========================================="
echo -e "  All Services Started!"
echo -e "==========================================${NC}"
echo ""
echo -e "${WHITE}Service URLs:${NC}"
echo -e "${GRAY}  - Credit Scoring:  http://localhost:8001${NC}"
echo -e "${GRAY}  - Fraud Detection: http://localhost:8002${NC}"
echo -e "${GRAY}  - Orchestrator:    http://localhost:8003${NC}"
echo -e "${GRAY}  - Data Enrichment: http://localhost:8004${NC}"
echo -e "${GRAY}  - Policy Engine:   http://localhost:8005${NC}"
echo -e "${GRAY}  - Report Generator: http://localhost:8006${NC}"
echo -e "${GRAY}  - Synthetic Data:  http://localhost:8007${NC}"
echo -e "${YELLOW}  - Augmented Scoring: http://localhost:8008${NC}"
echo -e "${GREEN}  - API Gateway:     http://localhost:8000${NC}"
echo -e "${GREEN}  - Next.js Client:  http://localhost:3000${NC}"
echo ""
echo -e "${CYAN}Press Ctrl+C to stop all services...${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping all services...${NC}"
    for pid in "${PIDS[@]}" "$CLIENT_PID"; do
        kill "$pid" 2>/dev/null || true
    done
    "$SCRIPT_DIR/kill-ports.sh" 2>/dev/null || true
    echo -e "${GREEN}All services stopped.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for user input
read -r
cleanup
