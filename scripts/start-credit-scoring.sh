#!/bin/bash
# Start CredsCore Credit Scoring Service
# Port: 8001

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_DIR="$(dirname "$SCRIPT_DIR")/services/credit_scoring"

echo "Starting Credit Scoring Service..."
echo "URL: http://localhost:8001"
echo "Health: http://localhost:8001/health"
echo "Docs: http://localhost:8001/docs"
echo ""

cd "$SERVICE_DIR" || exit 1
echo "Working directory: $(pwd)"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload 2>&1
