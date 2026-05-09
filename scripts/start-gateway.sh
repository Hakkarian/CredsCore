#!/bin/bash
# Start CredsCore API Gateway
# Port: 4000

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATEWAY_DIR="$(dirname "$SCRIPT_DIR")/services/api_gateway"

echo "Starting API Gateway..."
echo "URL: http://localhost:4000"
echo "Health: http://localhost:4000/health"
echo ""

cd "$GATEWAY_DIR"
python -m uvicorn main:app --host 0.0.0.0 --port 4000 --reload
