#!/bin/bash
# Start CredsCore Report Generator Service
# Port: 8004

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_DIR="$(dirname "$SCRIPT_DIR")/services/report-generator"

echo "Starting Report Generator Service..."
echo "URL: http://localhost:8004"
echo "Health: http://localhost:8004/health"
echo "Docs: http://localhost:8004/docs"
echo ""

cd "$SERVICE_DIR"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
