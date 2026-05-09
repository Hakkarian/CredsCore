#!/bin/bash
# Start CredsCore Orchestrator Service
# Port: 8005

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_DIR="$(dirname "$SCRIPT_DIR")/services/orchestrator"

echo "Starting Orchestrator Service..."
echo "URL: http://localhost:8005"
echo "Health: http://localhost:8005/health"
echo "Docs: http://localhost:8005/docs"
echo ""

cd "$SERVICE_DIR"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
