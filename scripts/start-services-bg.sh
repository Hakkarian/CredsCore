#!/bin/bash
# Start all CredsCore services in background (non-interactive)

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
echo -e " CredsCore - Starting All Services"
echo -e "==========================================${NC}"
echo ""

# Step 1: Kill existing processes
echo -e "${YELLOW}Step 1: Killing any existing processes on ports...${NC}"
bash "$SCRIPT_DIR/kill-ports.sh" 2>/dev/null || true
echo ""

# Step 2: Start services
echo -e "${YELLOW}Step 2: Starting services in background...${NC}"
echo ""

SERVICES=(
 "Credit Scoring:8001:start-credit-scoring.sh"
 "Fraud Detection:8002:start-fraud.sh"
 "Policy Engine:8003:start-policy.sh"
 "Report Generator:8004:start-reports.sh"
 "Orchestrator:8005:start-orchestrator.sh"
 "Data Enrichment:8006:start-enrichment.sh"
 "Synthetic Data:8007:start-synthetic-data.sh"
 "Augmented Scoring:8008:start-augmented-scoring.sh"
 "Social Capital:8009:start-social-capital.sh"
 "API Gateway:4000:start-gateway.sh"
)

PIDS=()
LOG_DIR="/tmp/credscore"
mkdir -p "$LOG_DIR"

for svc in "${SERVICES[@]}"; do
 IFS=':' read -r name port script <<< "$svc"
 echo -e " Starting ${GREEN}$name${NC} on port $port..."
 cd "$SCRIPT_DIR"
 nohup bash "$script" > "$LOG_DIR/${port}.log" 2>&1 &
 PIDS+=($!)
 sleep 1
done

echo ""
echo -e "${YELLOW}Step 3: Waiting for services to initialize (5s)...${NC}"
sleep 5
echo ""

echo -e "${CYAN}Service Status:${NC}"
echo "------------------------------------------"
for svc in "${SERVICES[@]}"; do
 IFS=':' read -r name port script <<< "$svc"
 if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
 echo -e " $name (port $port): ${GREEN}Running${NC}"
 else
 echo -e " $name (port $port): ${YELLOW}Starting...${NC}"
 fi
done
echo ""

# Step 4: Start client
echo -e "${YELLOW}Step 4: Starting Next.js client...${NC}"
cd "$PROJECT_ROOT/client"
nohup npm run dev > "$LOG_DIR/client.log" 2>&1 &
CLIENT_PID=$!
sleep 3
echo ""

echo -e "${CYAN}=========================================="
echo -e " All Services Started!"
echo -e "==========================================${NC}"
echo ""
echo -e "${GREEN}Service URLs:${NC}"
echo -e "${GRAY} - Credit Scoring: http://localhost:8001${NC}"
echo -e "${GRAY} - Fraud Detection: http://localhost:8002${NC}"
echo -e "${GRAY} - Policy Engine: http://localhost:8003${NC}"
echo -e "${GRAY} - Report Generator: http://localhost:8004${NC}"
echo -e "${GRAY} - Orchestrator: http://localhost:8005${NC}"
echo -e "${GRAY} - Data Enrichment: http://localhost:8006${NC}"
echo -e "${GRAY} - Synthetic Data: http://localhost:8007${NC}"
echo -e "${GRAY} - Augmented Scoring: http://localhost:8008${NC}"
echo -e "${GRAY} - Social Capital: http://localhost:8009${NC}"
echo -e "${GREEN} - API Gateway: http://localhost:4000${NC}"
echo -e "${GREEN} - Next.js Client: http://localhost:3000${NC}"
echo ""
echo -e "${CYAN}Log files: $LOG_DIR/*.log${NC}"
echo ""
echo -e "${CYAN}To stop all services, run: bash scripts/kill-ports.sh${NC}"
echo ""
