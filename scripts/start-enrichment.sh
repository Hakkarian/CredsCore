#!/bin/bash
# Start CredsCore Data Enrichment Service
# Port: 8006

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_DIR="$(dirname "$SCRIPT_DIR")/services/data-enrichment/src"

echo "Starting Data Enrichment Service..."
echo "URL: http://localhost:8006"
echo "Health: http://localhost:8006/health"
echo "Docs: http://localhost:8006/docs"
echo ""

cd "$SERVICE_DIR"
python -m uvicorn main:app --host 0.0.0.0 --port 8006 --reload
