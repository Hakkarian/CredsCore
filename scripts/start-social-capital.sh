#!/bin/bash
# Start CredsCore Social Capital Service
# Port: 8009

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_DIR="$(dirname "$SCRIPT_DIR")/services/social_capital"

echo "Starting Social Capital Service..."
echo "URL: http://localhost:8009"
echo "Health: http://localhost:8009/health"
echo ""

cd "$SERVICE_DIR"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8009 --reload
