#!/bin/bash
# Start CredsCore Policy Service
# Port: 8003

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_DIR="$(dirname "$SCRIPT_DIR")/services/policy"

echo "Starting Policy Service..."
echo "URL: http://localhost:8003"
echo "Health: http://localhost:8003/health"
echo "Docs: http://localhost:8003/docs"
echo ""

cd "$SERVICE_DIR"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
