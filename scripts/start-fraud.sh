#!/bin/bash
# Start CredsCore Fraud Detection Service
# Port: 8002

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_DIR="$(dirname "$SCRIPT_DIR")/services/fraud_detection"

echo "Starting Fraud Detection Service..."
echo "URL: http://localhost:8002"
echo "Health: http://localhost:8002/health"
echo "Docs: http://localhost:8002/docs"
echo ""

cd "$SERVICE_DIR"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
